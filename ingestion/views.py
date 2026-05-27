from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, DataSource, NormalizedActivity, RawRecord
from .normalizers import normalize_sap_row, normalize_travel_row, normalize_utility_row
from .parsers.sap_parsers import parse_sap_csv
from .parsers.travel_parsers import parse_travel_csv
from .parsers.utility_parsers import parse_utility_csv
from .serializers import (
    DataSourceUploadSerializer,
    NormalizedActivityEditSerializer,
    NormalizedActivityListSerializer,
)
from .validators import validate_sap_row, validate_travel_row, validate_utility_row


def _json_safe_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


class CSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    source_type = None
    parser = None
    validator = None
    normalizer = None

    def post(self, request, *args, **kwargs):
        serializer = DataSourceUploadSerializer(
            data=request.data,
            context={
                "request": request,
                "source_type": self.source_type,
            },
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            data_source = serializer.save()
            csv_rows = self.parser(serializer.validated_data["file"])

            raw_records_created = 0
            normalized_records_created = 0
            invalid_records = 0
            suspicious_records = 0

            for row_number, row in enumerate(csv_rows, start=1):
                raw_record = RawRecord.objects.create(
                    data_source=data_source,
                    row_number=row_number,
                    payload=row,
                    status=RawRecord.IngestionStatus.PENDING,
                )
                raw_records_created += 1

                validation_result = self.validator(row)
                if not validation_result["is_valid"]:
                    raw_record.status = RawRecord.IngestionStatus.INVALID
                    raw_record.validation_errors = validation_result["errors"]
                    raw_record.save(update_fields=["status", "validation_errors", "updated_at"])
                    invalid_records += 1
                    continue

                normalized_data = self.normalizer(row)
                NormalizedActivity.objects.create(
                    tenant=data_source.tenant,
                    raw_record=raw_record,
                    suspicious=validation_result["suspicious"],
                    flag_reason=validation_result["flag_reason"],
                    **normalized_data,
                )

                raw_record.status = RawRecord.IngestionStatus.NORMALIZED
                raw_record.validation_errors = []
                raw_record.save(update_fields=["status", "validation_errors", "updated_at"])

                normalized_records_created += 1
                if validation_result["suspicious"]:
                    suspicious_records += 1

        return Response(
            {
                "datasource_id": data_source.id,
                "raw_records_created": raw_records_created,
                "normalized_records_created": normalized_records_created,
                "invalid_records": invalid_records,
                "suspicious_records": suspicious_records,
            },
            status=status.HTTP_201_CREATED,
        )


class SAPUploadView(CSVUploadView):
    source_type = DataSource.SourceType.SAP
    parser = staticmethod(parse_sap_csv)
    validator = staticmethod(validate_sap_row)
    normalizer = staticmethod(normalize_sap_row)


class UtilityUploadView(CSVUploadView):
    source_type = DataSource.SourceType.UTILITY
    parser = staticmethod(parse_utility_csv)
    validator = staticmethod(validate_utility_row)
    normalizer = staticmethod(normalize_utility_row)


class TravelUploadView(CSVUploadView):
    source_type = DataSource.SourceType.TRAVEL
    parser = staticmethod(parse_travel_csv)
    validator = staticmethod(validate_travel_row)
    normalizer = staticmethod(normalize_travel_row)


class ActivityListView(generics.ListAPIView):
    serializer_class = NormalizedActivityListSerializer

    def get_queryset(self):
        return (
            NormalizedActivity.objects.select_related("raw_record__data_source")
            .all()
            .order_by("-created_at")
        )


class ActivityApproveView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        activity = get_object_or_404(NormalizedActivity, pk=pk)

        with transaction.atomic():
            old_value = {"review_status": activity.review_status}
            activity.review_status = NormalizedActivity.ReviewStatus.APPROVED
            activity.reviewed_at = timezone.now()
            activity.save(update_fields=["review_status", "reviewed_at", "updated_at"])

            AuditLog.objects.create(
                activity=activity,
                actor=None,
                action=AuditLog.Action.APPROVED,
                old_value=old_value,
                new_value={"review_status": activity.review_status},
            )

        return Response(NormalizedActivityListSerializer(activity).data)


class ActivityRejectView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        activity = get_object_or_404(NormalizedActivity, pk=pk)

        with transaction.atomic():
            old_value = {"review_status": activity.review_status}
            activity.review_status = NormalizedActivity.ReviewStatus.REJECTED
            activity.reviewed_at = timezone.now()
            activity.save(update_fields=["review_status", "reviewed_at", "updated_at"])

            AuditLog.objects.create(
                activity=activity,
                actor=None,
                action=AuditLog.Action.REJECTED,
                old_value=old_value,
                new_value={"review_status": activity.review_status},
            )

        return Response(NormalizedActivityListSerializer(activity).data)


class ActivityEditView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        activity = get_object_or_404(NormalizedActivity, pk=pk)
        serializer = NormalizedActivityEditSerializer(
            activity,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        old_value = {
            field: _json_safe_value(getattr(activity, field))
            for field in serializer.validated_data.keys()
        }

        with transaction.atomic():
            serializer.save()

            new_value = {
                field: _json_safe_value(getattr(serializer.instance, field))
                for field in serializer.validated_data.keys()
            }
            AuditLog.objects.create(
                activity=serializer.instance,
                actor=None,
                action=AuditLog.Action.UPDATED,
                old_value=old_value,
                new_value=new_value,
            )

        return Response(NormalizedActivityListSerializer(serializer.instance).data)

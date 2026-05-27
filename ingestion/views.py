from django.db import transaction
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataSource, RawRecord
from .parsers.sap_parsers import parse_sap_csv
from .parsers.travel_parsers import parse_travel_csv
from .parsers.utility_parsers import parse_utility_csv
from .serializers import DataSourceUploadSerializer


class CSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    source_type = None
    parser = None

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
            raw_records = [
                RawRecord(
                    data_source=data_source,
                    row_number=row_number,
                    payload=row,
                    status=RawRecord.IngestionStatus.PENDING,
                )
                for row_number, row in enumerate(csv_rows, start=1)
            ]
            RawRecord.objects.bulk_create(raw_records)

        return Response(
            {
                "datasource_id": data_source.id,
                "source_type": data_source.source_type,
                "filename": data_source.filename,
                "raw_records_created": len(raw_records),
            },
            status=status.HTTP_201_CREATED,
        )


class SAPUploadView(CSVUploadView):
    source_type = DataSource.SourceType.SAP
    parser = staticmethod(parse_sap_csv)


class UtilityUploadView(CSVUploadView):
    source_type = DataSource.SourceType.UTILITY
    parser = staticmethod(parse_utility_csv)


class TravelUploadView(CSVUploadView):
    source_type = DataSource.SourceType.TRAVEL
    parser = staticmethod(parse_travel_csv)

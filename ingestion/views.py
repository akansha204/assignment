from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataSource
from .serializers import DataSourceUploadSerializer


class CSVUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    source_type = None

    def post(self, request, *args, **kwargs):
        serializer = DataSourceUploadSerializer(
            data=request.data,
            context={
                "request": request,
                "source_type": self.source_type,
            },
        )
        serializer.is_valid(raise_exception=True)
        data_source = serializer.save()

        return Response(
            {
                "datasource_id": data_source.id,
                "filename": data_source.filename,
                "source_type": data_source.source_type,
                "status": "created",
            },
            status=status.HTTP_201_CREATED,
        )


class SAPUploadView(CSVUploadView):
    source_type = DataSource.SourceType.SAP


class UtilityUploadView(CSVUploadView):
    source_type = DataSource.SourceType.UTILITY


class TravelUploadView(CSVUploadView):
    source_type = DataSource.SourceType.TRAVEL

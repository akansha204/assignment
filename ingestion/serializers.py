from pathlib import Path

from rest_framework import serializers

from .models import DataSource, Tenant


class DataSourceUploadSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)

    def validate_file(self, uploaded_file):
        filename = Path(uploaded_file.name)
        if filename.suffix.lower() != ".csv":
            raise serializers.ValidationError("Only .csv files are supported.")
        return uploaded_file

    def validate(self, attrs):
        tenant = Tenant.objects.order_by("id").first()
        if tenant is None:
            raise serializers.ValidationError(
                {"tenant": "At least one tenant is required before uploading data."}
            )

        attrs["tenant"] = tenant
        return attrs

    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        request = self.context.get("request")
        source_type = self.context["source_type"]

        uploaded_by = None
        if request and request.user and request.user.is_authenticated:
            uploaded_by = request.user

        return DataSource.objects.create(
            tenant=validated_data["tenant"],
            source_type=source_type,
            ingestion_method=DataSource.IngestionMethod.CSV_UPLOAD,
            filename=Path(uploaded_file.name).name,
            uploaded_by=uploaded_by,
        )

from pathlib import Path

from rest_framework import serializers

from .models import DataSource, NormalizedActivity, Tenant


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


class NormalizedActivityListSerializer(serializers.ModelSerializer):
    source_type = serializers.CharField(source="raw_record.data_source.source_type", read_only=True)

    class Meta:
        model = NormalizedActivity
        fields = [
            "id",
            "source_type",
            "activity_type",
            "scope",
            "quantity",
            "unit",
            "normalized_quantity",
            "normalized_unit",
            "review_status",
            "suspicious",
            "flag_reason",
            "created_at",
        ]


class NormalizedActivityEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedActivity
        fields = [
            "quantity",
            "normalized_quantity",
            "unit",
            "normalized_unit",
            "flag_reason",
        ]
        extra_kwargs = {
            "quantity": {"required": False},
            "normalized_quantity": {"required": False},
            "unit": {"required": False},
            "normalized_unit": {"required": False},
            "flag_reason": {"required": False},
        }

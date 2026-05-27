from django.conf import settings
from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DataSource(models.Model):
    class SourceType(models.TextChoices):
        SAP = "sap", "SAP fuel/procurement"
        UTILITY = "utility", "Utility electricity"
        TRAVEL = "travel", "Corporate travel"

    class IngestionMethod(models.TextChoices):
        CSV_UPLOAD = "csv_upload", "CSV upload"
        API = "api", "API"
        MANUAL = "manual", "Manual"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="data_sources",
    )
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    ingestion_method = models.CharField(
        max_length=30,
        choices=IngestionMethod.choices,
        default=IngestionMethod.CSV_UPLOAD,
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_data_sources",
    )
    source_system = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["tenant", "source_type"]),
            models.Index(fields=["uploaded_at"]),
        ]

    def __str__(self):
        return f"{self.tenant} - {self.source_type} - {self.filename}"


class RawRecord(models.Model):
    class IngestionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VALID = "valid", "Valid"
        INVALID = "invalid", "Invalid"
        NORMALIZED = "normalized", "Normalized"
        SKIPPED = "skipped", "Skipped"

    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.CASCADE,
        related_name="raw_records",
    )
    row_number = models.PositiveIntegerField()
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=IngestionStatus.choices,
        default=IngestionStatus.PENDING,
    )
    validation_errors = models.JSONField(default=list, blank=True)
    source_record_id = models.CharField(max_length=255, blank=True)
    row_hash = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_source", "row_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["data_source", "row_number"],
                name="unique_raw_record_per_source_row",
            ),
        ]
        indexes = [
            models.Index(fields=["data_source", "status"]),
        ]

    def __str__(self):
        return f"{self.data_source_id} row {self.row_number}"


class NormalizedActivity(models.Model):
    class Scope(models.IntegerChoices):
        SCOPE_1 = 1, "Scope 1"
        SCOPE_2 = 2, "Scope 2"
        SCOPE_3 = 3, "Scope 3"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        NEEDS_INFO = "needs_info", "Needs information"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.PROTECT,
        related_name="normalized_activities",
    )
    raw_record = models.OneToOneField(
        RawRecord,
        on_delete=models.PROTECT,
        related_name="normalized_activity",
    )
    scope = models.PositiveSmallIntegerField(choices=Scope.choices)
    activity_type = models.CharField(max_length=100)
    activity_date = models.DateField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=6)
    unit = models.CharField(max_length=50)
    normalized_quantity = models.DecimalField(max_digits=18, decimal_places=6)
    normalized_unit = models.CharField(max_length=50)
    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    suspicious = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    normalized_payload = models.JSONField(default=dict, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_activities",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "scope"]),
            models.Index(fields=["tenant", "review_status"]),
            models.Index(fields=["suspicious"]),
        ]

    def __str__(self):
        return f"{self.tenant} - {self.activity_type} ({self.normalized_quantity} {self.normalized_unit})"


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        FLAGGED = "flagged", "Flagged"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMMENTED = "commented", "Commented"

    activity = models.ForeignKey(
        NormalizedActivity,
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_audit_logs",
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["activity", "timestamp"]),
            models.Index(fields=["actor", "timestamp"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.action} on activity {self.activity_id}"

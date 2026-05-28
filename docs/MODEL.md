# Backend Data Model

This prototype uses a small relational model to represent the ESG ingestion lifecycle:

```text
upload -> raw storage -> validation -> normalization -> analyst review -> audit logging
```

The model separates uploaded source data from normalized activity records so the system can preserve the original input while still providing a clean review surface.

## Tenant

Purpose:

`Tenant` represents the company or client whose ESG data is being ingested. It provides the base for multi-tenant awareness, even though the prototype uses a default demo tenant.

Important fields:

- `name`: Human-readable tenant name.
- `slug`: Stable unique identifier for the tenant.
- `is_active`: Allows tenants to be enabled or disabled.
- `created_at`, `updated_at`: Basic lifecycle timestamps.

Pipeline relationship:

Uploads and normalized activities are associated with a tenant. This makes it possible to scope data by organization as the prototype evolves.

## DataSource

Purpose:

`DataSource` represents an upload batch or source import. Each CSV upload creates one `DataSource` record.

Important fields:

- `tenant`: The tenant that owns the upload.
- `source_type`: Identifies the source as `sap`, `utility`, or `travel`.
- `ingestion_method`: Tracks how the data entered the system, currently `csv_upload`.
- `filename`: Original uploaded filename.
- `uploaded_at`: Upload timestamp.
- `uploaded_by`: Optional user who uploaded the file.
- `metadata`: JSON field for source-specific batch metadata.

Pipeline relationship:

`DataSource` is created at upload time and acts as the parent record for all raw rows parsed from that file.

## RawRecord

Purpose:

`RawRecord` preserves each original CSV row before validation or normalization. It is the source-of-truth copy for a single ingested row.

Important fields:

- `data_source`: Upload batch this row came from.
- `row_number`: Row position in the uploaded CSV.
- `payload`: Original row stored as JSON.
- `status`: Ingestion state such as `pending`, `invalid`, or `normalized`.
- `validation_errors`: JSON list of validation issues for invalid rows.
- `source_record_id`: Optional external source identifier.
- `row_hash`: Optional hash for duplicate detection or traceability.

Pipeline relationship:

After parsing, every row becomes a `RawRecord`. Validation updates its status and errors. Valid rows are then linked to a normalized activity.

## NormalizedActivity

Purpose:

`NormalizedActivity` is the canonical activity model used for analyst review. It converts source-specific rows into a common structure.

Important fields:

- `tenant`: Tenant that owns the activity.
- `raw_record`: One-to-one link back to the original source row.
- `scope`: ESG scope, represented as Scope 1, Scope 2, or Scope 3.
- `activity_type`: Canonical activity label, such as diesel fuel, electricity, or flight.
- `quantity`, `unit`: Original measured quantity and unit.
- `normalized_quantity`, `normalized_unit`: Cleaned quantity and unit for review/reporting.
- `review_status`: Analyst workflow state such as pending, approved, or rejected.
- `suspicious`: Marks valid records that need analyst attention.
- `flag_reason`: Explanation for suspicious records.
- `normalized_payload`: JSON field for additional normalized context.
- `reviewed_by`, `reviewed_at`: Optional review attribution and timestamp.

Pipeline relationship:

Valid raw records become `NormalizedActivity` rows. Analysts review these records instead of working directly with source-specific CSV payloads.

## AuditLog

Purpose:

`AuditLog` records review and edit actions performed on normalized activities.

Important fields:

- `activity`: The normalized activity affected by the action.
- `actor`: Optional user who performed the action.
- `action`: Action type such as `approved`, `rejected`, or `updated`.
- `old_value`: JSON snapshot before the change.
- `new_value`: JSON snapshot after the change.
- `timestamp`: Time the audit event occurred.

Pipeline relationship:

Audit logs are created during analyst review actions. They provide traceability for approvals, rejections, and edits.

## Ingestion Lifecycle

1. Upload: A CSV file is submitted through a source-specific API endpoint.
2. Raw storage: A `DataSource` is created, and each parsed CSV row is stored as a `RawRecord`.
3. Validation: Source-specific rules update raw records as invalid or eligible for normalization.
4. Normalization: Valid rows become `NormalizedActivity` records with canonical fields.
5. Analyst review: Activities can be approved, rejected, or edited.
6. Audit logging: Review and edit actions create `AuditLog` records for traceability.

This structure keeps the original uploaded data, validation outcome, normalized review object, and audit history distinct but connected.

# Tradeoffs and Prototype Limitations

This project was built as a four-day ESG ingestion prototype. The implementation focuses on demonstrating the core data flow: upload, parsing, validation, normalization, analyst review, and audit logging.

Several production concerns were intentionally simplified to keep the scope realistic and the system easy to evaluate.

## No Async Processing or Celery

CSV ingestion is processed synchronously during the upload request. Celery, Redis, queue workers, retry policies, and job status tracking were not added.

This is acceptable for the prototype because the sample files are small and the goal is to demonstrate the ingestion pipeline, not high-volume processing. In production, larger uploads should move to background jobs with progress tracking and retry handling.

## No Authentication or RBAC

The prototype does not implement authentication, role-based access control, or analyst-specific permissions. Review actions may store a null actor.

This keeps the focus on ingestion and review mechanics. In production, uploads, edits, approvals, rejections, and tenant access would need strict authorization and user attribution.

## SQLite Instead of PostgreSQL

SQLite was used for quick setup and simple local execution. It avoids provisioning a database and keeps the assignment easy to run.

This is not the right long-term choice for concurrent ingestion, larger datasets, tenant isolation, or operational reliability. PostgreSQL would be the preferred production database.

## No Background Jobs

The system does not include scheduled jobs, retry workers, reconciliation tasks, or delayed processing.

For a prototype, all meaningful behavior can be triggered directly from API requests. A production system would likely need background jobs for reprocessing, data quality checks, enrichment, file cleanup, and notification workflows.

## No Real SAP or OData Integrations

SAP data is represented through CSV exports rather than a live SAP or OData integration.

This avoids spending prototype time on credentials, network setup, enterprise system access, and connector-specific behavior. The model still leaves room to add real integrations later by treating each upload or import as a `DataSource`.

## CSV Uploads Instead of Live Enterprise Connectors

The ingestion interface is file-based. There are no live connectors for utility providers, travel systems, procurement systems, or cloud storage buckets.

CSV uploads are appropriate for this assignment because they are easy to inspect, test, and demonstrate. Production connectors would require more robust schema management, authentication, rate limiting, retries, and monitoring.

## Simplified Emission Normalization

Normalization maps source rows into canonical activity records, but it does not calculate emissions factors, CO2e, market-based versus location-based electricity, supplier-specific factors, or regional methodologies.

This keeps the prototype focused on ingestion architecture. A production ESG platform would need a much more detailed emissions calculation layer with versioned factors and methodology traceability.

## No Large-Scale Performance Optimizations

The implementation is not optimized for very large files, high concurrency, streaming ingestion, or bulk review operations.

This was acceptable because the assignment demonstrates correctness and clarity for small operational datasets. Scaling would require bulk database operations, streaming parsers, pagination, indexing review paths, async processing, and careful memory management.

## Limited Validation Coverage

Validation rules are intentionally narrow and source-specific. They check required fields, positive quantities, valid dates, and a small number of business constraints.

This is enough to show where validation belongs in the pipeline. A production version would need configurable schemas, richer type checks, duplicate detection, cross-field rules, source-specific tolerances, and explainable validation reports.

## No Audit Locking After Approval

Approved records can still be edited in the current prototype. The audit log records the change, but there is no locking or approval reversal workflow.

This keeps the review API simple. In production, approved records may need immutable states, controlled reopen workflows, stronger audit guarantees, or approval versioning.

## No Persistent Cloud Storage

The prototype preserves raw rows in the database but does not persist the original uploaded CSV file in cloud storage.

This is acceptable for a small demonstration, but production ingestion should store original files in durable object storage with checksums, metadata, retention policies, and access controls.

## Why These Tradeoffs Were Acceptable

For a four-day prototype assignment, the highest-value work was proving the data model and ingestion workflow end to end. The implementation shows how records move from raw source data into normalized activities, how invalid and suspicious rows are handled, and how analysts can review and audit changes.

The deferred areas are important, but they are mostly operational concerns that become necessary when the system moves beyond prototype scale. Keeping them out of scope made the project easier to reason about, easier to run locally, and more focused on the core ESG ingestion problem.

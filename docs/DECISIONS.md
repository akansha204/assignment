# Engineering Decisions

## CSV Ingestion

CSV ingestion was chosen because the expected source systems export operational data in tabular formats and CSV is the lowest-friction interface for a prototype. It lets the backend exercise the important parts of the ingestion pipeline without requiring live integrations with SAP, utility portals, or travel systems.

This also keeps the assignment focused on data handling: parsing, validation, normalization, review, and auditability.

## Synchronous Processing

Ingestion is handled synchronously during the upload request. For the current prototype scale, this is easier to understand, test, and demonstrate than introducing a queue, worker process, retry semantics, and job status tracking.

An async queue would be appropriate for larger files, long-running validation, external enrichment, or production reliability requirements. For this assignment, synchronous processing keeps the system simpler while preserving the shape of the pipeline.

## SQLite

SQLite was used to reduce setup cost and make the project easy to run locally or deploy as a small prototype. It avoids database provisioning and keeps migrations straightforward.

This is a prototype tradeoff. A production version should use PostgreSQL or another managed relational database, especially for concurrent uploads, larger datasets, tenant isolation, and operational reliability.

## Source-Specific Parsers

Parsers are separated by source type because SAP, utility, and travel files have different schemas and will likely evolve independently. Keeping parser modules separate makes source-specific behavior explicit and prevents one generic parser from accumulating conditional logic for every source.

The shared parsing approach is intentionally simple, but the module boundaries leave room for each source to gain its own cleanup, encoding handling, or schema support later.

## Raw Record Preservation

Raw CSV rows are stored before validation and normalization so the system keeps a source-of-truth copy of what was uploaded. This is important for auditability, debugging, reprocessing, and explaining why a row was rejected or transformed.

Preserving raw records also separates ingestion from interpretation. The original data remains available even if validation rules or normalization rules change later.

## Suspicious Records

Suspicious records are flagged instead of rejected when the data is usable but needs analyst attention. For example, a flight record with missing distance may still represent a real business activity, even if it is incomplete.

Rejecting these records too early would hide potentially important emissions activity. Flagging allows the pipeline to continue while making review risk visible.

## Canonical Activity Model

A canonical `NormalizedActivity` model exists so downstream review and reporting do not need to understand every source schema. SAP fuel purchases, utility electricity usage, and travel records can all be represented as activities with scope, activity type, quantity, unit, normalized quantity, and review status.

This model is intentionally modest. It supports the current review workflow without pretending to be a complete emissions accounting system.

## Django + React

Django REST Framework was selected because it provides a fast path to well-structured API endpoints, validation, models, migrations, and admin-friendly data handling. It is a good fit for a data ingestion backend where relational integrity and explicit models matter.

React was selected for the frontend because it works well for interactive upload and analyst review screens. Vite keeps the frontend setup lightweight, while Axios and Zustand provide simple API access and state management without adding much framework overhead.

## Lightweight Deployment

Deployment was kept lightweight using Gunicorn for the backend and a standard Vite build for the frontend. This matches the prototype goal: demonstrate a working full-stack ingestion flow without spending unnecessary effort on infrastructure.

A production deployment would need stronger configuration management, authentication, tenant-aware authorization, managed storage, background workers, observability, and a production database.

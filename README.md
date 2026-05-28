# ESG Data Ingestion Prototype

## 1. Project Overview

This project is a Django + React prototype for ingesting operational sustainability data from multiple enterprise sources. It supports CSV uploads from SAP fuel/procurement exports, utility electricity exports, and corporate travel exports.

The prototype demonstrates an end-to-end ESG data ingestion workflow:

```text
upload -> parsing -> validation -> normalization -> analyst review -> audit workflow
```

The system preserves raw uploaded rows, validates source-specific records, normalizes valid rows into a canonical activity model, flags suspicious activity, and supports analyst review actions such as approve, reject, and edit.

## 2. Architecture Overview

The application is split into a Django REST backend and a React frontend.

Backend responsibilities:

- Accept CSV uploads through source-specific API endpoints.
- Create upload batch records using `DataSource`.
- Preserve every original CSV row as a `RawRecord`.
- Validate records using source-specific validation rules.
- Normalize valid records into `NormalizedActivity`.
- Expose analyst review APIs.
- Record review and edit actions in `AuditLog`.

Frontend responsibilities:

- Provide a browser UI for uploading source files.
- Display normalized activities for analyst review.
- Support approve, reject, and edit workflows through API calls.

## 3. Ingestion Workflow

1. A user uploads a CSV file through one of the source-specific upload endpoints.
2. The backend creates or retrieves a default demo tenant.
3. A `DataSource` record is created for the upload batch.
4. The relevant parser reads the CSV using `csv.DictReader`.
5. Each CSV row is stored unchanged as a `RawRecord`.
6. Each row is validated using source-specific rules.
7. Invalid rows are marked as `invalid` and store validation errors.
8. Valid rows are normalized into `NormalizedActivity`.
9. Suspicious but valid rows are normalized and flagged for analyst review.
10. Analysts can approve, reject, or edit normalized activity records.
11. Review actions are captured in audit logs.

## 4. Source Types

The prototype supports three source types:

- `sap`: SAP fuel and procurement exports.
- `utility`: Utility electricity billing exports.
- `travel`: Corporate travel exports.

Each source type has its own upload endpoint, parser, validator, and normalizer.

## 5. Validation & Normalization

Validation is intentionally simple and source-specific.

SAP validation:

- `Plant Code` is required.
- `Quantity` must be greater than zero.
- `Posting Date` must be valid.
- `UOM` is required.

Utility validation:

- `Meter ID` is required.
- `kWh` must be greater than zero.
- `Billing End` must be after `Billing Start`.

Travel validation:

- `Traveler Name` is required.
- `Travel Type` is required.
- `Origin` is required.
- `Destination` is required for flights.
- Missing flight distance does not fail validation, but marks the activity as suspicious.

Normalization maps valid rows into a canonical activity shape with:

- ESG scope.
- Activity type.
- Original quantity and unit.
- Normalized quantity and unit.
- Review status.
- Suspicious flag and flag reason where applicable.

## 6. Review Workflow

Normalized activities enter the review workflow with a pending review status.

Analysts can:

- List normalized activities.
- Approve an activity.
- Reject an activity.
- Edit quantity, normalized quantity, unit, normalized unit, or flag reason.

Each approve, reject, or edit action creates an `AuditLog` entry. For prototype simplicity, audit actors may be stored as `null`.

## 7. Tech Stack

Backend:

- Django
- Django REST Framework
- SQLite
- Gunicorn

Frontend:

- React
- Vite
- Zustand
- Axios

## 8. Local Development Setup

Backend setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend setup:

```bash
cd web
npm install
npm run dev
```

By default, the Django API runs on:

```text
http://localhost:8000
```

The Vite frontend typically runs on:

```text
http://localhost:5173
```

## 9. API Endpoints

Upload endpoints:

```http
POST /api/upload/sap
POST /api/upload/utility
POST /api/upload/travel
```

Each upload endpoint accepts a multipart CSV file using the `file` field.

Example response:

```json
{
  "datasource_id": 1,
  "raw_records_created": 10,
  "normalized_records_created": 8,
  "invalid_records": 2,
  "suspicious_records": 1
}
```

Activity review endpoints:

```http
GET /api/activities
PATCH /api/activities/<id>/approve
PATCH /api/activities/<id>/reject
PATCH /api/activities/<id>/edit
```

Editable fields for activity edit:

```json
{
  "quantity": "100.000000",
  "normalized_quantity": "100.000000",
  "unit": "L",
  "normalized_unit": "liters",
  "flag_reason": "Updated during analyst review"
}
```

## 10. Deployment

The backend is configured for Gunicorn-based deployment using the included `Procfile`.

Typical deployment command:

```bash
gunicorn core.wsgi
```

The frontend can be built as a static Vite application:

```bash
cd web
npm run build
```

Deployment currently assumes a prototype environment. Production deployment would require additional hardening around environment variables, static file hosting, database configuration, authentication, authorization, logging, and monitoring.

## 11. Tradeoffs & Assumptions

- SQLite is used for prototype simplicity.
- A default demo tenant is automatically created for uploads.
- Authentication and tenant isolation are not fully implemented.
- CSV schemas are assumed to match the sample source files.
- Validation rules are intentionally minimal and source-specific.
- Normalization does not calculate emissions factors or CO2e values.
- Suspicious activity detection is limited to simple rule-based checks.
- Audit actors may be `null` in the current prototype.
- The system is designed to demonstrate ingestion architecture, not full production readiness.

## 12. Future Improvements

- Add authentication and role-based authorization.
- Implement real tenant selection and tenant-scoped access control.
- Move from SQLite to PostgreSQL.
- Add emissions factor mapping and CO2e calculations.
- Add richer validation with configurable source schemas.
- Add duplicate detection and idempotent re-ingestion.
- Add file storage for original uploaded CSV files.
- Add pagination, filtering, and search for activity review.
- Add detailed audit views in the frontend.
- Add automated tests for parsers, validators, normalizers, and review APIs.
- Add background processing for large uploads.
- Add deployment-grade logging, metrics, and error tracking.

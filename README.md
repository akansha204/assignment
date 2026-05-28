# ESG Data Ingestion Prototype

A Django + React prototype for ingesting operational sustainability datasets from SAP fuel/procurement exports, utility electricity exports, and corporate travel exports.

The system demonstrates the core ESG ingestion workflow:

```text
upload -> parsing -> validation -> normalization -> analyst review -> audit workflow
```

This project is a prototype designed for a 4-day engineering assignment and intentionally prioritizes clarity and workflow completeness over production-scale infrastructure.

## Architecture and Workflow

The backend exposes Django REST Framework APIs for CSV upload, validation, normalization, analyst review, and audit logging. Uploaded files are parsed into raw records first, then valid rows are transformed into canonical normalized activity records for review.

The frontend is a React + Vite application that supports CSV upload and analyst review actions through the backend APIs.

High-level flow:

1. Upload a source-specific CSV file.
2. Create a `DataSource` upload batch.
3. Preserve each CSV row as a `RawRecord`.
4. Run source-specific validation.
5. Normalize valid rows into `NormalizedActivity`.
6. Flag suspicious records for review.
7. Approve, reject, or edit activities.
8. Write review actions to `AuditLog`.

## Features

- Multi-source CSV ingestion.
- Source-specific parsers for SAP, utility, and travel data.
- Raw record preservation before validation and normalization.
- Validation and normalization pipelines.
- Suspicious activity detection.
- Analyst review workflow.
- Approve, reject, and edit actions.
- Audit logs for review and edit actions.
- Deployed frontend and backend prototype.

## Project Structure

```text
.
├── core/                 # Django project settings and root URLs
├── ingestion/            # Ingestion models, APIs, parsers, validators, normalizers
├── audit/                # Audit app scaffold
├── sample_data/          # Example SAP, utility, and travel CSV files
├── web/                  # React + Vite frontend
├── docs/                 # Engineering documentation
├── manage.py
├── requirements.txt
├── Procfile
└── README.md
```

## Tech Stack

Backend:

- Django REST Framework
- SQLite
- Gunicorn

Frontend:

- React + Vite
- Zustand
- Axios

## Local Development

Backend:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd web
npm install
npm run dev
```

Default local URLs:

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## API Summary

CSV upload endpoints:

```http
POST /api/upload/sap
POST /api/upload/utility
POST /api/upload/travel
```

Activity review endpoints:

```http
GET /api/activities
PATCH /api/activities/<id>/approve
PATCH /api/activities/<id>/reject
PATCH /api/activities/<id>/edit
```

Upload endpoints accept multipart form data with a `file` field containing a CSV file.

## Deployment

The backend is configured for lightweight Gunicorn deployment using the included `Procfile`.

```bash
gunicorn core.wsgi
```

The frontend can be built as a static Vite application:

```bash
cd web
npm run build
```

The deployment approach is intentionally lightweight for prototype evaluation. A production version would require stronger environment configuration, authentication, authorization, persistent storage, production database infrastructure, logging, monitoring, and background processing.

## Engineering Documentation

Detailed engineering notes are available in `/docs`:

- [DECISIONS.md](./docs/DECISIONS.md): Major implementation decisions and rationale.
- [TRADEOFFS.md](./docs/TRADEOFFS.md): Prototype limitations and intentionally deferred production concerns.
- [MODEL.md](./docs/MODEL.md): Backend data model and ingestion lifecycle.
- [SOURCES.md](./docs/SOURCES.md): Source data assumptions and research notes.

# Source Data Assumptions

This prototype simulates ESG ingestion from common operational data sources using CSV files. The goal is to model realistic ingestion patterns without depending on live enterprise integrations, proprietary schemas, or vendor-specific credentials.

## 1. SAP Export Formats

SAP data can reach downstream systems through several mechanisms, including flat file exports, IDoc-based integration, database/report extracts, and OData APIs depending on the SAP landscape and implementation.

For this prototype, SAP fuel/procurement data is represented as a CSV-style export with fields such as:

- Document number
- Material description
- Plant code
- Quantity
- Unit of measure
- Posting date
- Vendor

This shape is intended to approximate the kind of operational procurement or inventory movement data that may be relevant for Scope 1 fuel activity. It does not assume a specific SAP module, custom table, IDoc type, or OData service.

CSV was chosen because it allows the ingestion pipeline to demonstrate parsing, validation, raw row preservation, and normalization without requiring access to an SAP system.

## 2. Utility Electricity Datasets

Utility electricity data is commonly available through invoices, billing portals, account exports, spreadsheets, or third-party energy management tools. The exact format varies by provider and region.

The prototype assumes a utility billing export with fields such as:

- Meter ID
- Billing start date
- Billing end date
- kWh usage
- Tariff type
- Amount

These fields are enough to model a basic Scope 2 electricity ingestion flow. The prototype validates meter presence, positive electricity usage, and billing date order.

The implementation does not model more advanced utility concepts such as demand charges, time-of-use intervals, renewable energy certificates, market-based versus location-based accounting, or regional grid factor selection.

## 3. Corporate Travel Platforms

Corporate travel data may come from expense and travel platforms such as Concur, Navan, or similar systems. These platforms can expose exports or APIs depending on customer configuration and available integrations.

For the prototype, travel data is represented as a CSV export with fields such as:

- Traveler name
- Travel type
- Origin
- Destination
- Distance in kilometers
- Cost

This shape is intended to support simple Scope 3 activity modeling for flights, hotels, and ground transport. It does not assume any proprietary vendor schema or private platform behavior.

Missing flight distance is treated as suspicious rather than invalid because the trip may still represent a real activity that requires analyst review.

## Prototype Ingestion Choices

CSV-style exports were simulated because they are easy to inspect, upload, and test within a short prototype assignment. They also reflect a common early-stage integration pattern for ESG data programs, where operational teams often start with exported reports before moving to automated connectors.

The ingestion design keeps source-specific parsing separate while preserving each raw row before validation and normalization. This makes it possible to support future sources or richer connectors without losing traceability back to the original input.

In a production system, these CSV sources could be replaced or supplemented with:

- SAP OData or IDoc-based integrations.
- Scheduled file drops from enterprise systems.
- Utility provider APIs or managed energy data platforms.
- Travel and expense platform APIs.
- Cloud storage ingestion from approved data exchange locations.

Those integrations were intentionally left out of scope so the prototype could focus on the core ingestion workflow and data model.

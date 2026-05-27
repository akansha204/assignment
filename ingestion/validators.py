from datetime import datetime
from decimal import Decimal, InvalidOperation


def _value(row, field_name):
    value = row.get(field_name)
    if value is None:
        return ""
    return str(value).strip()


def _is_positive_decimal(value):
    try:
        return Decimal(value) > 0
    except (InvalidOperation, TypeError):
        return False


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def validate_sap_row(row):
    errors = []

    if not _value(row, "Plant Code"):
        errors.append("Plant Code is required.")

    if not _is_positive_decimal(_value(row, "Quantity")):
        errors.append("Quantity must be greater than 0.")

    if not _parse_date(_value(row, "Posting Date")):
        errors.append("Posting Date must be a valid date.")

    if not _value(row, "UOM"):
        errors.append("Unit is required.")

    return {
        "is_valid": not errors,
        "errors": errors,
        "suspicious": False,
        "flag_reason": "",
    }


def validate_utility_row(row):
    errors = []
    billing_start = _parse_date(_value(row, "Billing Start"))
    billing_end = _parse_date(_value(row, "Billing End"))

    if not _value(row, "Meter ID"):
        errors.append("Meter ID is required.")

    if not _is_positive_decimal(_value(row, "kWh")):
        errors.append("kWh must be greater than 0.")

    if not billing_start:
        errors.append("Billing Start must be a valid date.")

    if not billing_end:
        errors.append("Billing End must be a valid date.")

    if billing_start and billing_end and billing_end <= billing_start:
        errors.append("Billing End must be after Billing Start.")

    return {
        "is_valid": not errors,
        "errors": errors,
        "suspicious": False,
        "flag_reason": "",
    }


def validate_travel_row(row):
    errors = []
    suspicious = False
    flag_reason = ""
    travel_type = _value(row, "Travel Type")
    distance = _value(row, "Distance KM")

    if not _value(row, "Traveler Name"):
        errors.append("Traveler is required.")

    if not travel_type:
        errors.append("Travel Type is required.")

    if not _value(row, "Origin"):
        errors.append("Origin is required.")

    if travel_type.lower() == "flight" and not _value(row, "Destination"):
        errors.append("Destination is required for flights.")

    if travel_type.lower() == "flight" and not distance:
        suspicious = True
        flag_reason = "Missing flight distance."

    return {
        "is_valid": not errors,
        "errors": errors,
        "suspicious": suspicious,
        "flag_reason": flag_reason,
    }

from datetime import datetime
from decimal import Decimal, InvalidOperation

from .models import NormalizedActivity


UNIT_MAP = {
    "l": "liters",
    "m3": "cubic_meter",
}


def _value(row, field_name):
    value = row.get(field_name)
    if value is None:
        return ""
    return str(value).strip()


def _decimal(value, default="0"):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return Decimal(default)


def _date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def normalize_sap_row(row):
    quantity = _decimal(_value(row, "Quantity"))
    unit = _value(row, "UOM")

    return {
        "scope": NormalizedActivity.Scope.SCOPE_1,
        "activity_type": _value(row, "Material Description"),
        "activity_date": _date(_value(row, "Posting Date")),
        "quantity": quantity,
        "unit": unit,
        "normalized_quantity": quantity,
        "normalized_unit": UNIT_MAP.get(unit.lower(), unit),
        "normalized_payload": {
            "source_type": "sap",
            "plant_code": _value(row, "Plant Code"),
            "vendor": _value(row, "Vendor"),
            "document_number": _value(row, "Document Number"),
        },
    }


def normalize_utility_row(row):
    quantity = _decimal(_value(row, "kWh"))

    return {
        "scope": NormalizedActivity.Scope.SCOPE_2,
        "activity_type": "electricity",
        "activity_date": _date(_value(row, "Billing End")),
        "quantity": quantity,
        "unit": "kWh",
        "normalized_quantity": quantity,
        "normalized_unit": "kwh",
        "normalized_payload": {
            "source_type": "utility",
            "meter_id": _value(row, "Meter ID"),
            "billing_start": _value(row, "Billing Start"),
            "billing_end": _value(row, "Billing End"),
            "tariff_type": _value(row, "Tariff Type"),
        },
    }


def normalize_travel_row(row):
    distance = _value(row, "Distance KM")
    quantity = _decimal(distance)

    return {
        "scope": NormalizedActivity.Scope.SCOPE_3,
        "activity_type": _value(row, "Travel Type"),
        "activity_date": None,
        "quantity": quantity,
        "unit": "km" if distance else "",
        "normalized_quantity": quantity,
        "normalized_unit": "km" if distance else "",
        "normalized_payload": {
            "source_type": "travel",
            "traveler": _value(row, "Traveler Name"),
            "origin": _value(row, "Origin"),
            "destination": _value(row, "Destination"),
            "cost": _value(row, "Cost"),
        },
    }

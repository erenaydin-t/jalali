"""Document event handlers to keep Jalali/Gregorian dates in sync."""
from __future__ import annotations

from typing import Iterable

import frappe
from frappe.model.document import Document

from . import calendar
from . import settings


DATE_FIELD_TYPES = {"Date", "Datetime", "DateTime"}


def _iter_date_fields(doc: Document) -> Iterable[str]:
    meta = doc.meta
    for df in meta.get("fields", []):
        if df.fieldtype in DATE_FIELD_TYPES:
            yield df.fieldname
        if df.fieldtype == "Table":
            table_rows = doc.get(df.fieldname) or []
            for row in table_rows:
                if isinstance(row, Document):
                    convert_dates_to_gregorian(row)


def convert_dates_to_gregorian(doc: Document, method: str | None = None) -> None:
    """Convert Jalali date strings coming from the UI into Gregorian before save."""
    if getattr(doc, "_jalali_dates_converted", False):
        return
    if doc.doctype == "Jalali Settings":
        return
    if not settings.user_prefers_jalali():
        return

    for fieldname in _iter_date_fields(doc):
        value = doc.get(fieldname)
        if not value:
            continue
        converted = calendar.convert_user_input_to_gregorian(value)
        if converted and converted != value:
            doc.set(fieldname, converted)

    setattr(doc, "_jalali_dates_converted", True)

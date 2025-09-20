"""Monkey patches to bridge Jalali support into frappe formatting stack."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable

import frappe

from . import calendar
from . import settings

_original_formatdate: Callable[..., Any] | None = None
_original_format_datetime: Callable[..., Any] | None = None
_original_formatters: dict[str, Callable[..., Any]] | None = None


def _should_render_jalali() -> bool:
    try:
        return settings.user_prefers_jalali()
    except Exception:
        return False


def _make_formatter_wrapper(original: Callable[..., Any], calendar_key: str) -> Callable[..., Any]:
    include_time = calendar_key.lower() != "date"

    @wraps(original)
    def wrapper(value, df=None, doc=None, translated=False, **kwargs):
        if _should_render_jalali():
            formatted = calendar.convert_to_jalali_display(value, include_time)
            if formatted:
                return formatted
        return original(value, df=df, doc=doc, translated=translated, **kwargs)

    return wrapper


def _patch_formatters():
    global _original_formatters
    if _original_formatters is not None:
        return
    if not hasattr(frappe, "formatters"):
        return
    _original_formatters = {}

    for key in ("Date", "Datetime", "DateTime"):
        if key in frappe.formatters:
            _original_formatters[key] = frappe.formatters[key]
            frappe.formatters[key] = _make_formatter_wrapper(frappe.formatters[key], key)


def _patch_formatdate():
    global _original_formatdate
    if _original_formatdate is not None:
        return

    _original_formatdate = frappe.utils.data.formatdate

    @wraps(_original_formatdate)
    def wrapper(value, df=None, string: bool = False, translated: bool = False, **kwargs):
        if _should_render_jalali():
            formatted = calendar.convert_to_jalali_display(value, include_time=False)
            if formatted:
                return formatted
        return _original_formatdate(value, df=df, string=string, translated=translated, **kwargs)

    frappe.utils.data.formatdate = wrapper


def _patch_format_datetime():
    global _original_format_datetime
    if _original_format_datetime is not None:
        return

    _original_format_datetime = frappe.utils.data.format_datetime

    @wraps(_original_format_datetime)
    def wrapper(value, df=None, string: bool = False, translated: bool = False, **kwargs):
        if _should_render_jalali():
            formatted = calendar.convert_to_jalali_display(value, include_time=True)
            if formatted:
                return formatted
        return _original_format_datetime(value, df=df, string=string, translated=translated, **kwargs)

    frappe.utils.data.format_datetime = wrapper


def apply_runtime_patches():
    if not settings.is_enabled():
        return
    _patch_formatdate()
    _patch_format_datetime()
    _patch_formatters()


_APPLIED_ONCE = False


def ensure_runtime_patches():
    global _APPLIED_ONCE
    if not _APPLIED_ONCE:
        apply_runtime_patches()
        _APPLIED_ONCE = True

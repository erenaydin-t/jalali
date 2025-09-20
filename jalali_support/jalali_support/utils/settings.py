"""Helpers to read Jalali Support configuration and user preferences."""
from __future__ import annotations

import contextlib
from typing import Optional

import frappe
from frappe.utils import cint


def _get_settings_doc():
    if not frappe.db:
        return None
    with contextlib.suppress(frappe.DoesNotExistError, Exception):
        return frappe.get_cached_doc("Jalali Settings", "Jalali Settings")
    return None


def is_enabled() -> bool:
    settings = _get_settings_doc()
    if settings:
        return bool(cint(settings.enable_jalali))
    conf = frappe.conf.get("enable_jalali_calendar")
    if conf is not None:
        return bool(conf)
    return False


def get_default_calendar() -> str:
    settings = _get_settings_doc()
    if settings and cint(settings.enable_jalali):
        return (settings.default_calendar or "Jalali").lower()
    conf = frappe.conf.get("default_calendar")
    if conf:
        return str(conf).lower()
    return "gregorian"


def allow_user_override() -> bool:
    settings = _get_settings_doc()
    if settings:
        return bool(cint(settings.allow_user_override))
    conf = frappe.conf.get("jalali_allow_user_override")
    if conf is not None:
        return bool(conf)
    return True


def get_user_calendar(user: Optional[str] = None) -> str:
    """Return active calendar for user ("gregorian" or "jalali")."""
    if not is_enabled():
        return "gregorian"

    user = user or getattr(getattr(frappe.local, "session", None), "user", None)
    if not user:
        user = "Guest"

    if allow_user_override() and user not in {"Guest"}:
        with contextlib.suppress(Exception):
            from frappe.defaults import get_user_default

            user_pref = get_user_default("calendar_preference", user)
            if user_pref:
                return str(user_pref).lower()

    return get_default_calendar()


def user_prefers_jalali(user: Optional[str] = None) -> bool:
    return get_user_calendar(user) == "jalali"

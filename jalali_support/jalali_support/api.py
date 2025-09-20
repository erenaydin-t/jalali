from __future__ import annotations

import frappe
from frappe import _

from .utils import settings


@frappe.whitelist()
def set_user_calendar(calendar: str):
    """Persist the user''s preferred calendar ("jalali" or "gregorian")."""
    if not settings.is_enabled():
        frappe.throw(_("Jalali calendar support is not enabled."))

    if not settings.allow_user_override():
        frappe.throw(_("Per-user calendar selection is disabled."))

    calendar = (calendar or "").strip().lower()
    if calendar not in {"jalali", "gregorian"}:
        frappe.throw(_("Invalid calendar value."))

    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please sign in before changing calendar settings."))

    if calendar == "gregorian":
        frappe.defaults.clear_user_default("calendar_preference", user)
    else:
        frappe.defaults.set_user_default("calendar_preference", calendar, user)

    frappe.publish_realtime(
        "workflow:calendar-preference-changed",
        {"user": user, "calendar": calendar},
        after_commit=True,
    )

    return {"calendar": calendar}

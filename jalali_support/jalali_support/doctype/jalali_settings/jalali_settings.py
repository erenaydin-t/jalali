import frappe
from frappe import _
from frappe.model.document import Document


class JalaliSettings(Document):
    VALID_CALENDARS = {"gregorian", "jalali"}

    def validate(self):
        if self.default_calendar:
            normalized = self.default_calendar.strip().lower()
            if normalized not in self.VALID_CALENDARS:
                frappe.throw(_("Default calendar must be Jalali or Gregorian."))
            self.default_calendar = normalized.title()

    def on_update(self):
        frappe.cache().hdel("jalali_support", "boot")
        frappe.clear_cache(doctype=self.doctype)
        # Notify connected clients so they refresh their calendar preference.
        frappe.publish_realtime(
            "workflow:calendar-preference-changed",
            {
                "calendar": (self.default_calendar or "jalali").strip().lower(),
                "user": "system",
            },
            user="Administrator",
            after_commit=True,
        )

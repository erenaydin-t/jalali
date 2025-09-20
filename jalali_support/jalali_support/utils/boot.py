"""Boot hooks to expose Jalali settings to the client."""
from __future__ import annotations

from . import settings


def boot_session(bootinfo):
    try:
        enabled = settings.is_enabled()
        calendar_pref = settings.get_user_calendar()
        allow_override = settings.allow_user_override()
    except Exception:
        enabled = False
        calendar_pref = "gregorian"
        allow_override = True

    bootinfo.jalali_support = {
        "enabled": enabled,
        "calendar": calendar_pref,
        "allow_user_override": allow_override,
    }

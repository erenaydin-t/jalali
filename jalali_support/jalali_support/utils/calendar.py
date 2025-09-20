"""Jalali (Persian) calendar helper utilities used across the app."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional, Tuple, Union

JALALI_MONTH_NAMES = [
    "Farvardin",
    "Ordibehesht",
    "Khordad",
    "Tir",
    "Mordad",
    "Shahrivar",
    "Mehr",
    "Aban",
    "Azar",
    "Dey",
    "Bahman",
    "Esfand",
]

_GREG_DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
_JALALI_DAYS_IN_MONTH = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

_JALALI_DATE_RE = re.compile(
    r"^(?P<y>[12]\d{3})[-/.](?P<m>0?[1-9]|1[0-2])[-/.](?P<d>0?[1-9]|[12]\d|3[01])"
    r"(?:\s+(?P<h>\d{1,2}):(?P<mi>\d{2})(?::(?P<s>\d{2}))?)?$"
)


DateLike = Union[str, date, datetime]


def _is_leap_gregorian(year: int) -> bool:
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def gregorian_to_jalali(year: int, month: int, day: int) -> Tuple[int, int, int]:
    gy = year - 1600
    gm = month - 1
    gd = day - 1

    g_day_no = 365 * gy
    g_day_no += (gy + 3) // 4
    g_day_no -= (gy + 99) // 100
    g_day_no += (gy + 399) // 400

    for i in range(gm):
        g_day_no += _GREG_DAYS_IN_MONTH[i]
    if gm >= 2 and _is_leap_gregorian(year):
        g_day_no += 1
    g_day_no += gd

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    for i, month_len in enumerate(_JALALI_DAYS_IN_MONTH):
        if j_day_no < month_len:
            jm = i + 1
            jd = j_day_no + 1
            break
        j_day_no -= month_len
    else:
        jm = 12
        jd = j_day_no + 1

    return jy, jm, jd


def jalali_to_gregorian(year: int, month: int, day: int) -> Tuple[int, int, int]:
    jy = year - 979
    jm = month - 1
    jd = day - 1

    j_day_no = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4
    for i in range(jm):
        j_day_no += _JALALI_DAYS_IN_MONTH[i]
    j_day_no += jd

    g_day_no = j_day_no + 79

    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no %= 146097

    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100 * (g_day_no // 36524)
        g_day_no %= 36524

        if g_day_no >= 365:
            g_day_no += 1
        else:
            leap = False

    gy += 4 * (g_day_no // 1461)
    g_day_no %= 1461

    if g_day_no >= 366:
        leap = False
        g_day_no -= 1
        gy += g_day_no // 365
        g_day_no %= 365

    gd = g_day_no + 1

    months = _GREG_DAYS_IN_MONTH.copy()
    months[1] = 29 if leap or _is_leap_gregorian(gy) else 28

    gm = 0
    while gm < 12 and gd > months[gm]:
        gd -= months[gm]
        gm += 1

    return gy, gm + 1, gd


def split_datetime_string(value: str) -> Tuple[str, Optional[str]]:
    if " " in value:
        date_part, time_part = value.split(" ", 1)
        return date_part.strip(), time_part.strip() or None
    return value.strip(), None


def _sanitize_separator(value: str) -> str:
    return value.replace("/", "-").replace(".", "-")


def parse_jalali_date(value: str) -> Tuple[int, int, int]:
    match = _JALALI_DATE_RE.match(_sanitize_separator(value))
    if not match:
        raise ValueError(f"Not a valid Jalali date: {value}")
    year = int(match.group("y"))
    month = int(match.group("m"))
    day = int(match.group("d"))
    if year >= 1700:
        raise ValueError("Year looks Gregorian; refusing to parse as Jalali")
    return year, month, day


def parse_date(value: DateLike) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    value = value.strip()
    sanitized, time_part = split_datetime_string(value)
    if is_jalali_date(value):
        jy, jm, jd = parse_jalali_date(sanitized)
        gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
        if time_part:
            h, mi, *s = time_part.split(":")
            seconds = int(s[0]) if s else 0
            return datetime(gy, gm, gd, int(h), int(mi), seconds)
        return datetime(gy, gm, gd)
    sanitized = _sanitize_separator(value)
    return datetime.fromisoformat(sanitized)


def format_as_jalali(value: DateLike, with_time: bool = False) -> str:
    dt = parse_date(value)
    jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
    base = f"{jy:04d}-{jm:02d}-{jd:02d}"
    if with_time:
        return f"{base} {dt:%H:%M:%S}"
    return base


def format_as_gregorian(value: DateLike, with_time: bool = False) -> str:
    dt = parse_date(value)
    base = f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}"
    if with_time:
        return f"{base} {dt:%H:%M:%S}"
    return base


def is_jalali_date(value: DateLike) -> bool:
    if isinstance(value, (date, datetime)):
        return False
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value or value.lower() == "today":
        return False
    match = _JALALI_DATE_RE.match(_sanitize_separator(value))
    if not match:
        return False
    year = int(match.group("y"))
    return year < 1700


def convert_user_input_to_gregorian(value: DateLike) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, datetime):
        return format_as_gregorian(value, with_time=True)
    if isinstance(value, date):
        return format_as_gregorian(value)
    value = value.strip()
    if not value:
        return None
    sanitized = _sanitize_separator(value)
    if is_jalali_date(sanitized):
        date_part, time_part = split_datetime_string(sanitized)
        jy, jm, jd = parse_jalali_date(date_part)
        gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
        if time_part:
            h, mi, *s = time_part.split(":")
            seconds = int(s[0]) if s else 0
            return f"{gy:04d}-{gm:02d}-{gd:02d} {int(h):02d}:{int(mi):02d}:{seconds:02d}"
        return f"{gy:04d}-{gm:02d}-{gd:02d}"
    return sanitized


def convert_to_jalali_display(value: DateLike, include_time: bool = False) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return format_as_jalali(value, with_time=include_time)
    except Exception:
        return str(value)

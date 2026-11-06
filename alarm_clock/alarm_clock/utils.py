"""Small helper functions shared across the alarm clock package."""

from datetime import datetime


def parse_time(value: str) -> str:
    """Convert user input into a 24-hour ``"HH:MM"`` string.

    Accepted formats (case-insensitive, spaces ignored):
        ``"7"``, ``"7:30"``, ``"07:30"``, ``"7:30am"``, ``"7:30 pm"``,
        ``"12:00am"``, ``"19:45"``.

    Raises:
        ValueError: if the value cannot be interpreted as a valid time.
    """
    clean = value.strip().lower().replace(" ", "")
    if not clean:
        raise ValueError("Time cannot be empty.")

    # Remember an optional am/pm suffix and strip it from the string.
    am_pm = None
    if clean.endswith("am"):
        am_pm = "am"
        clean = clean[:-2]
    elif clean.endswith("pm"):
        am_pm = "pm"
        clean = clean[:-2]

    if ":" in clean:
        parts = clean.split(":")
        if len(parts) != 2:
            raise ValueError(f"{value!r} is not a valid time.")
        hour_str, minute_str = parts
    else:
        hour_str, minute_str = clean, "0"

    if not (hour_str.isdigit() and minute_str.isdigit()):
        raise ValueError(f"{value!r} is not a valid time.")

    hour = int(hour_str)
    minute = int(minute_str)

    # Convert 12-hour clock to 24-hour clock.
    if am_pm == "am" and hour == 12:
        hour = 0
    elif am_pm == "pm" and 1 <= hour <= 11:
        hour = (hour + 12) % 24

    if not 0 <= hour <= 23:
        raise ValueError(f"Hour {hour} is out of range 0-23.")
    if not 0 <= minute <= 59:
        raise ValueError(f"Minute {minute} is out of range 0-59.")

    return f"{hour:02d}:{minute:02d}"


def format_seconds(total_seconds: int) -> str:
    """Render a number of seconds as ``"Hh MMm SSs"`` or ``"now"``."""
    total_seconds = max(0, int(total_seconds))
    if total_seconds == 0:
        return "now"
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return " ".join(parts)
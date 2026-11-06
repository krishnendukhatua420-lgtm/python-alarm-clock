"""Alarm data model and the :class:`AlarmManager` that owns the alarm list."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .utils import parse_time


@dataclass
class Alarm:
    """A single alarm definition.

    Attributes:
        time: 24-hour time as ``"HH:MM"``.
        label: optional human-readable description.
        enabled: when ``False`` the alarm is silenced but kept.
        repeat_daily: ``True`` = fires every day, ``False`` = one shot.
        id: unique identifier assigned by :class:`AlarmManager`.
    """

    time: str
    label: str = ""
    enabled: bool = True
    repeat_daily: bool = True
    id: int = field(default=0, compare=False)

    def __post_init__(self) -> None:
        # Validate and normalise the time on creation/deserialisation.
        self.time = parse_time(self.time)

    @property
    def display(self) -> str:
        """Human-readable, one-line description of this alarm."""
        status = "ON " if self.enabled else "OFF"
        repeat = "daily" if self.repeat_daily else "once"
        tag = f' ("{self.label}")' if self.label else ""
        return f"[{status}] {self.time} {repeat}{tag}"

    def next_firing(self) -> datetime:
        """The next :class:`datetime` this alarm fires (counting from now)."""
        now = datetime.now()
        hour, minute = (int(part) for part in self.time.split(":"))
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    def seconds_until(self) -> int:
        """Whole seconds remaining until :meth:`next_firing`."""
        delta = self.next_firing() - datetime.now()
        return max(0, int(delta.total_seconds()))

    def to_dict(self) -> dict:
        return {
            "time": self.time,
            "label": self.label,
            "enabled": self.enabled,
            "repeat_daily": self.repeat_daily,
        }

    @classmethod
    def from_dict(cls, data: dict, alarm_id: int) -> "Alarm":
        return cls(
            time=data["time"],
            label=data.get("label", ""),
            enabled=data.get("enabled", True),
            repeat_daily=data.get("repeat_daily", True),
            id=alarm_id,
        )


class AlarmManager:
    """Owns the collection of alarms and assigns unique ids."""

    def __init__(self) -> None:
        self.alarms: list[Alarm] = []
        self._next_id = 1

    def add(self, time: str, label: str = "", repeat_daily: bool = True) -> Alarm:
        """Create, register and return a new alarm."""
        alarm = Alarm(time=time, label=label, repeat_daily=repeat_daily, id=self._next_id)
        self._next_id += 1
        self.alarms.append(alarm)
        self.alarms.sort(key=lambda item: item.time)
        return alarm

    def remove(self, alarm_id: int) -> bool:
        """Remove the alarm with ``alarm_id``; ``True`` if one was removed."""
        for index, alarm in enumerate(self.alarms):
            if alarm.id == alarm_id:
                del self.alarms[index]
                return True
        return False

    def toggle(self, alarm_id: int) -> bool:
        """Flip the enabled flag of the matching alarm; ``False`` if not found."""
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                alarm.enabled = not alarm.enabled
                return True
        return False

    def get(self, alarm_id: int) -> Alarm | None:
        """Return the alarm with ``alarm_id`` or ``None``."""
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

    def load_from_list(self, data: list[dict]) -> None:
        """Populate the manager from a list of dictionaries (JSON payload)."""
        self.alarms.clear()
        self._next_id = 1
        for item in data:
            alarm = Alarm.from_dict(item, alarm_id=self._next_id)
            self._next_id += 1
            self.alarms.append(alarm)
        self.alarms.sort(key=lambda entry: entry.time)
"""JSON-backed persistence of alarms and application settings."""

from __future__ import annotations

import json
from pathlib import Path

from .alarm import AlarmManager

DEFAULT_CONFIG_PATH = Path("alarm_clock_config.json")

DEFAULT_SETTINGS: dict = {
    "ringtone": "default",
    "duration": 8.0,  # seconds of sound per firing
}


class Config:
    """Loads and saves ``alarms`` + ``settings`` to a single JSON file."""

    def __init__(self, path: Path | str = DEFAULT_CONFIG_PATH) -> None:
        self.path = Path(path)
        self.manager = AlarmManager()
        self.settings: dict = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self) -> None:
        """Read the JSON file (if present and valid) into memory."""
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            # A corrupt/missing file is not fatal - start with defaults.
            return

        if not isinstance(data, dict):
            return

        self.settings.update(data.get("settings", {}))
        alarms_data = data.get("alarms", [])
        if isinstance(alarms_data, list):
            self.manager.load_from_list(alarms_data)

    def save(self) -> None:
        """Write the current alarms and settings to the JSON file."""
        payload = {
            "settings": self.settings,
            "alarms": [alarm.to_dict() for alarm in self.manager.alarms],
        }
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
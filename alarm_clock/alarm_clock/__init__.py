"""Alarm Clock application package.

Provides the building blocks used by the ``main.py`` entry point:
* :mod:`alarm_clock.utils` - time parsing helpers
* :mod:`alarm_clock.alarm` - the :class:`Alarm` model and :class:`AlarmManager`
* :mod:`alarm_clock.config` - JSON-backed persistence of alarms and settings
* :mod:`alarm_clock.sound`  - cross-platform alarm sound playback
"""

__version__ = "1.0.0"
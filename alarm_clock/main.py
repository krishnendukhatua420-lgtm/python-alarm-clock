"""Alarm Clock - command line entry point.

Run with::

    python main.py

The app shows a text menu while a background thread watches the clock and
rings any enabled alarm whose time has arrived.
"""

from __future__ import annotations

from datetime import datetime
import threading

from alarm_clock.config import Config
from alarm_clock.sound import SoundPlayer
from alarm_clock.utils import format_seconds, parse_time

MENU = """
================= ALARM CLOCK =================
 1. List alarms
 2. Add alarm
 3. Remove alarm
 4. Toggle alarm on/off
 5. Next firing time
 0. Quit
-----------------------------------------------"""


class AlarmClockApp:
    """Wires configuration, the sound player and the alarm monitor together."""

    def __init__(self, config_path: str = "alarm_clock_config.json") -> None:
        self.config = Config(config_path)
        self.player = SoundPlayer()
        self._stop = threading.Event()
        self._fired_today: dict[int, str] = {}  # alarm id -> "YYYY-MM-DD"
        self._monitor = threading.Thread(
            target=self._monitor_loop, name="alarm-monitor", daemon=True
        )

    # ------------------------------------------------------------- public
    def run(self) -> None:
        """Start the monitor thread and the interactive menu."""
        self._monitor.start()
        print("\nWelcome! The alarm clock is now ARMED. Press Ctrl+C to quit.\n")

        try:
            while True:
                print(MENU)
                choice = input("Choose an option: ").strip()
                if choice == "1":
                    self._list_alarms()
                elif choice == "2":
                    self._add_alarm()
                elif choice == "3":
                    self._remove_alarm()
                elif choice == "4":
                    self._toggle_alarm()
                elif choice == "5":
                    self._show_next()
                elif choice == "0":
                    break
                else:
                    print("Unknown option, please choose 0-5.")
        except KeyboardInterrupt:
            print("\n\nInterrupted - stopping...")
        finally:
            self._stop.set()
            self.config.save()
            print("Settings saved. Goodbye!")

    # ---------------------------------------------------------- menu acts
    def _list_alarms(self) -> None:
        alarms = self.config.manager.alarms
        if not alarms:
            print("No alarms set yet.")
            return
        for alarm in alarms:
            print(f"  #{alarm.id}: {alarm.display}")

    def _add_alarm(self) -> None:
        raw = input("Time (e.g. 7, 07:30, 7:30am, 19:45): ").strip()
        try:
            time_str = parse_time(raw)
        except ValueError as exc:
            print(f"Invalid time: {exc}")
            return

        label = input("Label (optional, Enter to skip): ").strip()
        repeat = input("Repeat daily? [Y/n]: ").strip().lower() != "n"
        alarm = self.config.manager.add(time_str, label=label, repeat_daily=repeat)
        self.config.save()
        print(f"Alarm #{alarm.id} set for {alarm.time}.")

    def _remove_alarm(self) -> None:
        self._list_alarms()
        raw = input("Alarm id to remove: ").strip()
        if not raw.isdigit():
            print("Invalid id.")
            return
        if self.config.manager.remove(int(raw)):
            self.config.save()
            print("Alarm removed.")
        else:
            print("No alarm with that id.")

    def _toggle_alarm(self) -> None:
        self._list_alarms()
        raw = input("Alarm id to toggle: ").strip()
        if not raw.isdigit():
            print("Invalid id.")
            return
        if self.config.manager.toggle(int(raw)):
            self.config.save()
            print("Alarm toggled.")
        else:
            print("No alarm with that id.")

    def _show_next(self) -> None:
        alarms = self.config.manager.alarms
        if not alarms:
            print("No alarms set yet.")
            return
        upcoming = min(alarms, key=lambda item: item.next_firing())
        print(
            f"Next alarm #{upcoming.id} at {upcoming.time} "
            f"(in {format_seconds(upcoming.seconds_until())})."
        )

    # -------------------------------------------------------- background
    def _monitor_loop(self) -> None:
        """Watch the clock every second and ring matching alarms once/day."""
        while not self._stop.is_set():
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            minute_str = now.strftime("%H:%M")

            for alarm in self.config.manager.alarms:
                if not alarm.enabled or alarm.time != minute_str:
                    continue
                if self._fired_today.get(alarm.id) == today:
                    continue  # already rang for this time today
                self._fired_today[alarm.id] = today
                self._ring(alarm)

            self._stop.wait(1.0)

    def _ring(self, alarm) -> None:
        """Announce an alarm and play the ringtone for the configured time."""
        banner = f"*** ALARM #{alarm.id} at {alarm.time} - wake up!"
        if alarm.label:
            banner += f" ({alarm.label})"
        print("\n" + "!" * 46)
        print(banner)
        print("!" * 46)
        try:
            duration = float(self.config.settings.get("duration", 8.0))
            self.player.play_ringtone(duration_seconds=duration)
        except (KeyboardInterrupt, OSError) as exc:  # beep may fail on odd HW
            print(f"Ringtone stopped: {exc}")


if __name__ == "__main__":
    AlarmClockApp().run()
"""Plays the alarm sound using only the Python standard library.

On Windows the :mod:`winsound` module provides precise square-wave beeps
(the ``alarm_clock`` project is Windows-first). On other platforms we fall
back to a console bell (``\\a``) so the code still runs without errors.
"""

from __future__ import annotations

import time

try:
    import winsound  # type: ignore[import-not-found]  # Windows only
except ImportError:  # pragma: no cover - macOS/Linux
    winsound = None


# A short three-tone "wake up" fseq: (frequency_hz, duration_ms).
_RINGTONE_PATTERN: tuple[tuple[int, int], ...] = (
    (880, 200),
    (0, 120),
    (988, 200),
    (0, 120),
    (1047, 250),
    (0, 300),
)


class SoundPlayer:
    """Plays beep patterns; non-Windows platforms get a silent-ish console bell."""

    def __init__(self) -> None:
        self.available = winsound is not None

    def beep(self, frequency: int = 880, duration_ms: int = 200) -> None:
        """Emit one beep tone (blocking). Frequency 0 means silent pause."""
        if frequency <= 0:
            time.sleep(duration_ms / 1000.0)
            return
        if winsound is not None:
            freq = max(37, min(32767, frequency))  # winsound frequency limits
            winsound.Beep(freq, duration_ms)
        else:
            print("\a", end="", flush=True)  # console bell fallback
            time.sleep(duration_ms / 1000.0)

    def play_ringtone(self, duration_seconds: float = 8.0) -> None:
        """Loop the ringtone melody for (at most) ``duration_seconds``."""
        deadline = time.monotonic() + max(0.0, duration_seconds)
        while time.monotonic() < deadline:
            for frequency, duration_ms in _RINGTONE_PATTERN:
                if time.monotonic() >= deadline:
                    return
                self.beep(frequency, duration_ms)
# ⏰ Alarm Clock

A dependency-free **command line alarm clock** written in Python with clean
separation into multiple sub-files.

## Features

- Set one-time or **daily repeating** alarms (24h or 12h input: `7`, `7:30`,
  `7:30am`, `19:45`).
- Add labels, enable/disable and remove alarms.
- Alarms ring with a beeping tone (uses `winsound` on Windows, terminal bell
  elsewhere) while a background thread watches the clock.
- Every alarm fires **once per day**, then waits for the next match.
- All alarms and settings are saved to `alarm_clock_config.json`, so your
  setup survives restarts.

## Project layout

```text
alarm_clock/
├── main.py                  # Entry point: menu + alarm monitor thread
├── requirements.txt         # No third-party deps (stdlib only)
├── README.md
└── alarm_clock/
    ├── __init__.py          # Package marker + version
    ├── utils.py             # parse_time() & format_seconds()
    ├── alarm.py             # Alarm dataclass + AlarmManager
    ├── config.py            # JSON persistence (alarms + settings)
    └── sound.py             # SoundPlayer (winsound / console bell)
```

## Usage

```console
python main.py
```

Then use the menu:

```text
1. List alarms
2. Add alarm            ->  Time (e.g. 7, 07:30, 7:30am, 19:45):
                           Label (optional, Enter to skip):
                           Repeat daily? [Y/n]:
3. Remove alarm
4. Toggle alarm on/off
5. Next firing time
0. Quit
```

## Quick test (non-interactive)

```console
python -c "from alarm_clock.utils import parse_time; print(parse_time('7:30pm'))"
# 19:30
```
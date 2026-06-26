# Alarm Clock — LLD Assignment

A command-line alarm clock built in Python, demonstrating clean layered architecture with persistent storage, background scheduling, and snooze/dismiss functionality.

---

## Features

- Add one-time or daily repeating alarms
- Persistent storage via a local JSON file (survives restarts)
- Background scheduler checks every second and rings at the exact minute
- Snooze (3 min) or dismiss a ringing alarm from the same menu
- Input validation for time (HH:MM) and date (DD/MM/YYYY)

---

## Architecture

```
main.py                  ← CLI entry point + input loop
│
├── AlarmService         ← Business logic (add, delete, snooze, match)
│   └── AlarmDao         ← JSON persistence (read/write alarm.json)
│       └── Alarm        ← Dataclass model
│
├── AlarmScheduler       ← Daemon thread, polls every second
└── BeepService          ← Daemon thread, plays terminal bell
```

### Design decisions

| Decision | Reason |
|---|---|
| Separate DAO from Service | Swap storage backend (e.g. SQLite) without touching business logic |
| Scheduler as daemon thread | Exits automatically when the main thread ends; no explicit cleanup needed |
| `(alarm_id, time)` dedup key | Same alarm can re-trigger after snooze without a session restart |
| Persist on every mutation | Keeps disk state always consistent; alarm count is low so cost is negligible |

---

## Project Structure

```
alarm_clock/
├── main.py
├── models/
│   └── alarm.py          # Alarm dataclass
├── services/
│   ├── alarm_dao.py      # JSON read/write
│   ├── alarm_service.py  # Business logic + validation
│   ├── alarm_scheduler.py# Background polling thread
│   └── sound_service.py  # Terminal bell thread
├── data/
│   └── alarm.json        # Persisted alarms (auto-created)
└── README.md
```

---

## Getting Started

**Requirements:** Python 3.10+, no third-party dependencies.

```bash
git clone https://github.com/hgupta2363/alarm-clock-assignment.git
cd alarm-clock-assignment
python3 main.py
```

---

## Usage

```
===== Alarm Clock =====
1. Add Alarm
2. List Alarms
3. Delete Alarm
4. Exit
(s/d when alarm is ringing to Snooze / Dismiss)
```

| Input | Action |
|---|---|
| `1` | Add a new alarm (prompts for time, date, daily flag) |
| `2` | List all active alarms |
| `3` | Delete an alarm by ID |
| `4` | Exit the application |
| `s` | Snooze the ringing alarm by 3 minutes |
| `d` | Dismiss the ringing alarm |

### Example session

```
Enter choice: 1
Enter time (HH:MM): 07:30
Enter date (DD/MM/YYYY): 26/06/2026
Daily? (y/n): y
Alarm added (ID 1).

Enter choice: 2
  ID=1  TIME=07:30  REPEAT=daily

🔔  ALARM RINGING — 07:30  (ID 1)
  s  →  Snooze 3 min
  d  →  Dismiss
Enter choice: s
Snoozed for 3 minutes.
```

---

## Class Reference

| Class | File | Responsibility |
|---|---|---|
| `Alarm` | `models/alarm.py` | Data model (id, time, date, daily, enabled) |
| `AlarmDao` | `services/alarm_dao.py` | Load/save alarms to `data/alarm.json` |
| `AlarmService` | `services/alarm_service.py` | Add, delete, snooze, match alarms |
| `AlarmScheduler` | `services/alarm_scheduler.py` | Poll every second; trigger, snooze, dismiss |
| `BeepService` | `services/sound_service.py` | Play/stop terminal bell sound |

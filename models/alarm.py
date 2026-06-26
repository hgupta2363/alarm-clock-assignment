from dataclasses import dataclass


@dataclass
class Alarm:
    """Represents a single alarm entry.

    Attributes:
        id: Unique integer identifier for the alarm.
        time: Trigger time in "HH:MM" (24-hour) format.
        enabled: Whether the alarm is active and will be evaluated by the scheduler.
        daily: If True, the alarm fires every day at the given time regardless of date.
        date: Target date in "DD/MM/YYYY" format; used only when daily is False.
    """

    id: int
    time: str
    enabled: bool
    daily: bool
    date: str

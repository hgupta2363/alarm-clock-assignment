import re
from datetime import datetime, timedelta

from models.alarm import Alarm
from services.alarm_dao import AlarmDao


def validate_time(time_str: str):
    """Validate that *time_str* is a well-formed HH:MM time string.

    Args:
        time_str: The string to validate.

    Raises:
        ValueError: If the format is wrong or the time value is invalid.
    """
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        raise ValueError("Time must be in HH:MM format")
    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValueError("Invalid time value")


def validate_date(date_str: str):
    """Validate that *date_str* is a well-formed DD/MM/YYYY date string.

    Args:
        date_str: The string to validate.

    Raises:
        ValueError: If the format is wrong or the date value is invalid.
    """
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        raise ValueError("Date must be in DD/MM/YYYY format")
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        raise ValueError("Invalid date value")


class AlarmService:
    """Business-logic layer that sits between the CLI / scheduler and the DAO.

    Handles alarm creation, deletion, snoozing, and matching the current time
    against the set of active alarms.
    """

    def __init__(self):
        self.dao = AlarmDao("data/alarm.json")
        self.dao.load_alarms_in_memory()

    def _next_id(self) -> int:
        """Return the next available unique alarm id."""
        alarms = self.dao.alarms
        if not alarms:
            return 1
        return max(alarm.id for alarm in alarms) + 1

    def add_new_alarm(self, time: str, date: str, daily: bool = False) -> Alarm:
        """Create and persist a new enabled alarm.

        Args:
            time: Trigger time in "HH:MM" format.
            date: Target date in "DD/MM/YYYY" format.
            daily: When True the alarm repeats every day; the *date* field is
                stored but not checked during matching.

        Returns:
            The newly created :class:`Alarm` instance.

        Raises:
            ValueError: If *time* or *date* fail format/value validation.
        """
        validate_date(date)
        validate_time(time)
        alarm = Alarm(
            id=self._next_id(),
            time=time,
            daily=daily,
            enabled=True,
            date=date,
        )
        self.dao.add_new_alarm(alarm)
        return alarm

    def snooze_alarm(self, alarm_id: int, minutes: int):
        """Postpone an alarm by *minutes* minutes and persist the change.

        Args:
            alarm_id: Id of the alarm to snooze.
            minutes: Number of minutes to add to the alarm's current time.

        Raises:
            ValueError: If no alarm with *alarm_id* exists.
        """
        alarm = self.dao.get_alarm_by_id(alarm_id)
        if alarm is None:
            raise ValueError(f"Alarm {alarm_id} not found")
        new_time = datetime.strptime(alarm.time, "%H:%M") + timedelta(minutes=minutes)
        alarm.time = new_time.strftime("%H:%M")
        self.dao.update_alarm(alarm)

    def get_matching_alarm(self) -> Alarm | None:
        """Return the first active alarm whose time matches the current minute.

        An alarm matches when:
        * it is enabled, **and**
        * its ``time`` equals the current HH:MM, **and**
        * it is ``daily`` *or* its ``date`` equals today's date.

        Returns:
            The matching :class:`Alarm`, or ``None`` if none matches.
        """
        now = datetime.now()
        now_hhmm = now.strftime("%H:%M")
        now_date = now.strftime("%d/%m/%Y")
        for alarm in self.dao.get_all_active_alarms():
            if alarm.time == now_hhmm and (alarm.daily or alarm.date == now_date):
                return alarm
        return None

    def get_all_alarms(self) -> list[Alarm]:
        """Return all currently enabled alarms."""
        return self.dao.get_all_active_alarms()

    def delete_alarm(self, alarm_id: int):
        """Remove an alarm by id.

        Args:
            alarm_id: Id of the alarm to delete.

        Raises:
            Exception: If no alarm with *alarm_id* exists.
        """
        self.dao.delete_alarm(alarm_id)

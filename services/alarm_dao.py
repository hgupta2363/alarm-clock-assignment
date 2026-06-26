import json
import os
from dataclasses import asdict
from models.alarm import Alarm


class AlarmDao:
    """Data-access object that persists alarms to a JSON file and caches them in memory.

    The file is read once at startup via ``load_alarms_in_memory`` and written
    back after every mutating operation so the on-disk state stays in sync.
    """

    def __init__(self, file_path: str):
        """
        Args:
            file_path: Path to the JSON file used for persistence.
        """
        self.file_path = file_path
        self.alarms: list[Alarm] = []

    def load_alarms_in_memory(self):
        """Read alarms from the JSON file into the in-memory list.

        Silently returns without error when the file does not yet exist (first run).

        Raises:
            Exception: If the file exists but cannot be parsed as valid JSON.
        """
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse alarm data: {e}") from e
            self.alarms = [Alarm(**alarm) for alarm in data]

    def _persist(self):
        """Serialize the in-memory alarm list and write it to disk."""
        with open(self.file_path, "w") as f:
            json.dump([asdict(alarm) for alarm in self.alarms], f, indent=4)

    def get_all_active_alarms(self) -> list[Alarm]:
        """Return all alarms whose ``enabled`` flag is True."""
        return [alarm for alarm in self.alarms if alarm.enabled]

    def add_new_alarm(self, alarm: Alarm):
        """Append a new alarm and persist to disk.

        Args:
            alarm: The alarm to add. Its ``id`` must be unique.
        """
        self.alarms.append(alarm)
        self._persist()

    def delete_alarm(self, alarm_id: int):
        """Remove the alarm with the given id and persist to disk.

        Args:
            alarm_id: The id of the alarm to remove.

        Raises:
            Exception: If no alarm with ``alarm_id`` exists.
        """
        if not any(alarm.id == alarm_id for alarm in self.alarms):
            raise Exception(f"Alarm id {alarm_id} not found")
        self.alarms = [alarm for alarm in self.alarms if alarm.id != alarm_id]
        self._persist()

    def update_alarm(self, updated_alarm: Alarm):
        """Replace an existing alarm record in place and persist to disk.

        If no alarm with a matching id is found the call is a no-op.

        Args:
            updated_alarm: Alarm instance containing the new field values. The
                ``id`` field is used to locate the existing record.
        """
        for i, alarm in enumerate(self.alarms):
            if alarm.id == updated_alarm.id:
                self.alarms[i] = updated_alarm
                self._persist()
                return

    def get_alarm_by_id(self, alarm_id: int) -> Alarm | None:
        """Look up a single alarm by its id.

        Args:
            alarm_id: The id to search for.

        Returns:
            The matching :class:`Alarm` instance, or ``None`` if not found.
        """
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

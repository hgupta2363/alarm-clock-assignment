import time

from models.alarm import Alarm


class AlarmScheduler:
    """Background scheduler that polls for matching alarms once per second.

    The scheduler runs in its own thread (started from ``main.py``) and
    communicates with the main thread by printing prompts to stdout. The main
    thread feeds user input back via the menu loop.

    Attributes:
        running: Controls the polling loop; set to False to stop the thread.
        current_alarm: The alarm currently ringing, or None when silent.
    """

    # Number of minutes added to a snoozed alarm.
    SNOOZE_MINUTES = 3

    def __init__(self, alarm_service, beep_service):
        """
        Args:
            alarm_service: :class:`AlarmService` instance used to look up and
                update alarms.
            beep_service: :class:`BeepService` instance used to play/stop the
                alert sound.
        """
        self.alarm_service = alarm_service
        self.beep_service = beep_service
        self.running = False
        self.current_alarm: Alarm | None = None
        # Tracks (alarm_id, HH:MM) pairs so the same alarm is not re-triggered
        # within the same minute but *will* fire again on the next occurrence.
        self._triggered: set[tuple[int, str]] = set()

    def start(self):
        """Enter the polling loop. Blocks until :meth:`stop` is called.

        Checks for a matching alarm every second. When one is found and has not
        already been triggered for the current minute it is fired.
        """
        self.running = True
        while self.running:
            alarm = self.alarm_service.get_matching_alarm()
            if alarm:
                key = (alarm.id, alarm.time)
                if key not in self._triggered:
                    self._trigger_alarm(alarm)
            time.sleep(1)

    def _trigger_alarm(self, alarm: Alarm):
        """Sound the alarm and print the action prompt.

        Args:
            alarm: The alarm that matched the current time.
        """
        self.current_alarm = alarm
        self._triggered.add((alarm.id, alarm.time))
        self.beep_service.start()
        print(f"\n🔔  ALARM RINGING — {alarm.time}  (ID {alarm.id})")
        print("  s  →  Snooze 3 min")
        print("  d  →  Dismiss")

    def dismiss_alarm(self):
        """Stop the beep and clear the current alarm state."""
        self.beep_service.stop()
        self.current_alarm = None

    def snooze_alarm(self):
        """Postpone the current alarm by :attr:`SNOOZE_MINUTES` and silence it.

        The alarm's new time is written to disk so the scheduler will re-trigger
        it once the new minute arrives.

        Raises:
            RuntimeError: If there is no alarm currently ringing.
        """
        if self.current_alarm is None:
            raise RuntimeError("No alarm is currently ringing")
        self.alarm_service.snooze_alarm(self.current_alarm.id, self.SNOOZE_MINUTES)
        # Remove from triggered so it fires again at the new time.
        self._triggered.discard((self.current_alarm.id, self.current_alarm.time))
        self.dismiss_alarm()

    def stop(self):
        """Signal the polling loop to exit on its next iteration."""
        self.running = False

    def get_current_alarm(self) -> Alarm | None:
        """Return the alarm currently ringing, or None if silent."""
        return self.current_alarm

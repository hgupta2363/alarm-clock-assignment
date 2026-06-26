import sys
import threading
import time


class BeepService:
    """Plays a repeating terminal bell in a background daemon thread.

    Usage::

        svc = BeepService()
        svc.start()   # begins beeping
        svc.stop()    # silences immediately
    """

    # Seconds between each bell character.
    BEEP_INTERVAL = 0.5

    def __init__(self):
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        """Start the beep loop in a daemon thread.

        Calling ``start`` when the service is already running is a no-op.
        """
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._beep_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the beep loop to stop. Returns immediately; the thread exits on its next iteration."""
        self._running = False

    def _beep_loop(self):
        """Internal loop that writes the ASCII bell character at regular intervals."""
        while self._running:
            sys.stdout.write("\a")
            sys.stdout.flush()
            time.sleep(self.BEEP_INTERVAL)

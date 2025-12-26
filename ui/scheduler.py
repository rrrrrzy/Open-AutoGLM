"""Scheduler for Phone Agent UI."""

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TaskScheduler(QObject):
    """Manage scheduled task execution."""

    task_triggered = pyqtSignal()

    def __init__(self):
        """Initialize task scheduler."""
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.task_triggered.emit)
        self._interval = 60  # Default 60 minutes
        self._enabled = False

    def set_interval(self, minutes: int):
        """Set the interval between task executions in minutes."""
        self._interval = minutes
        if self._enabled:
            self.timer.setInterval(minutes * 60 * 1000)  # Convert to milliseconds

    def get_interval(self) -> int:
        """Get the current interval in minutes."""
        return self._interval

    def start(self):
        """Start the scheduler."""
        if not self._enabled:
            self._enabled = True
            self.timer.start(self._interval * 60 * 1000)

    def stop(self):
        """Stop the scheduler."""
        if self._enabled:
            self._enabled = False
            self.timer.stop()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._enabled

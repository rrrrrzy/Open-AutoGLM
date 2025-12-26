"""Scheduler for Phone Agent UI."""

from datetime import datetime, time, timedelta
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TaskScheduler(QObject):
    """Manage scheduled task execution."""

    task_triggered = pyqtSignal()

    def __init__(self):
        """Initialize task scheduler."""
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_timeout)
        self._interval = 60  # Default 60 minutes
        self._enabled = False
        self._mode = "interval"  # "interval" or "specific_time"
        self._specific_time: Optional[time] = None  # For specific time mode
        self._last_execution: Optional[datetime] = None

    def set_interval(self, minutes: int):
        """Set the interval between task executions in minutes."""
        self._interval = minutes
        self._mode = "interval"
        if self._enabled:
            self.timer.stop()
            self.timer.start(minutes * 60 * 1000)  # Convert to milliseconds

    def set_specific_time(self, hour: int, minute: int):
        """
        Set specific time for daily execution.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        self._specific_time = time(hour, minute)
        self._mode = "specific_time"
        if self._enabled:
            self._schedule_next_execution()

    def get_interval(self) -> int:
        """Get the current interval in minutes."""
        return self._interval

    def get_mode(self) -> str:
        """Get the current scheduler mode."""
        return self._mode

    def get_specific_time(self) -> Optional[time]:
        """Get the specific time setting."""
        return self._specific_time

    def _schedule_next_execution(self):
        """Calculate and schedule next execution for specific time mode."""
        if self._mode != "specific_time" or self._specific_time is None:
            return

        now = datetime.now()
        target = datetime.combine(now.date(), self._specific_time)

        # If target time has passed today, schedule for tomorrow
        if target <= now:
            target += timedelta(days=1)

        # Calculate milliseconds until target time
        delay_ms = int((target - now).total_seconds() * 1000)
        
        self.timer.stop()
        self.timer.setSingleShot(True)
        self.timer.start(delay_ms)

    def _on_timer_timeout(self):
        """Handle timer timeout."""
        self._last_execution = datetime.now()
        self.task_triggered.emit()

        # Reschedule for specific time mode
        if self._mode == "specific_time":
            self._schedule_next_execution()

    def start(self):
        """Start the scheduler."""
        if not self._enabled:
            self._enabled = True
            if self._mode == "interval":
                self.timer.setSingleShot(False)
                self.timer.start(self._interval * 60 * 1000)
            else:  # specific_time
                self._schedule_next_execution()

    def stop(self):
        """Stop the scheduler."""
        if self._enabled:
            self._enabled = False
            self.timer.stop()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._enabled

    def get_next_execution_time(self) -> Optional[datetime]:
        """Get the next scheduled execution time."""
        if not self._enabled:
            return None

        if self._mode == "interval":
            if self._last_execution:
                return self._last_execution + timedelta(minutes=self._interval)
            else:
                return datetime.now() + timedelta(minutes=self._interval)
        else:  # specific_time
            if self._specific_time:
                now = datetime.now()
                target = datetime.combine(now.date(), self._specific_time)
                if target <= now:
                    target += timedelta(days=1)
                return target
        
        return None

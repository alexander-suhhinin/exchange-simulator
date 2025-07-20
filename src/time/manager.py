"""
Time Manager for simulation time control
"""
from datetime import datetime, timedelta
from typing import Optional, Callable, List
import time

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class TimeManager:
    """
    Manages simulation time and provides time-based utilities
    """

    def __init__(self, start_time: Optional[datetime] = None):
        """
        Initialize TimeManager

        Args:
            start_time: Starting time for simulation (defaults to earliest data available)
        """
        self._current_time = start_time or datetime.now()
        self._start_time = self._current_time
        self._time_step = timedelta(minutes=1)  # 1-minute steps
        self._callbacks: List[Callable] = []

    @property
    def current_time(self) -> datetime:
        """Get current simulation time"""
        return self._current_time

    @property
    def start_time(self) -> datetime:
        """Get simulation start time"""
        return self._start_time

    def set_current_time(self, new_time: datetime):
        """
        Set current simulation time

        Args:
            new_time: New current time
        """
        old_time = self._current_time
        self._current_time = new_time
        logger.info(f"Time advanced from {old_time} to {new_time}")

        # Execute callbacks
        for callback in self._callbacks:
            try:
                callback(old_time, new_time)
            except Exception as e:
                logger.error(f"Error in time callback: {e}")

    def advance_time(self, steps: int = 1):
        """
        Advance simulation time by specified number of steps

        Args:
            steps: Number of time steps to advance
        """
        new_time = self._current_time + (self._time_step * steps)
        self.set_current_time(new_time)

    def advance_to_next_candle(self):
        """Advance to the next 1-minute candle boundary"""
        # Calculate next minute boundary
        next_minute = self._current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        self.set_current_time(next_minute)

    def get_5m_boundary_time(self) -> datetime:
        """
        Get the current 5-minute boundary time

        Returns:
            Current 5-minute boundary datetime
        """
        minutes_since_epoch = self._current_time.minute + self._current_time.hour * 60
        boundary_minute = (minutes_since_epoch // 5) * 5
        return self._current_time.replace(minute=boundary_minute, second=0, microsecond=0)

    def should_include_next_candle(self) -> bool:
        """
        Determine if we should include the next 1m candle in 5m resampling

        Returns:
            True if next candle should be included
        """
        seconds = self._current_time.second
        return seconds >= 30

    def add_time_callback(self, callback: Callable[[datetime, datetime], None]):
        """
        Add a callback to be executed when time advances

        Args:
            callback: Function to call with (old_time, new_time)
        """
        self._callbacks.append(callback)

    def get_timestamp_ms(self) -> int:
        """
        Get current time as milliseconds timestamp

        Returns:
            Current time in milliseconds since epoch
        """
        return int(self._current_time.timestamp() * 1000)

    def format_time_for_api(self) -> str:
        """
        Format current time for API responses

        Returns:
            Formatted time string
        """
        return self._current_time.strftime("%Y-%m-%d %H:%M:%S")
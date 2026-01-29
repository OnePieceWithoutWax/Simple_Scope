"""
Lightweight logging module for Simple Scope application.
Logs are stored in-memory and cleared on startup.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional
from enum import IntEnum
from pathlib import Path


class LogLevel(IntEnum):
    """Log severity levels"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


@dataclass
class LogEntry:
    """A single log entry"""
    timestamp: str
    level: str
    source: str
    message: str

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level:<7} [{self.source}] {self.message}"


class Logger:
    """Simple in-memory logger with callback support for GUI updates."""

    def __init__(self, min_level: LogLevel = LogLevel.DEBUG):
        self._entries: List[LogEntry] = []
        self._min_level = min_level
        self._callbacks: List[Callable[[LogEntry], None]] = []

    @property
    def entries(self) -> List[LogEntry]:
        """Read-only access to log entries."""
        return self._entries.copy()

    @property
    def min_level(self) -> LogLevel:
        """Current minimum log level."""
        return self._min_level

    @min_level.setter
    def min_level(self, level: LogLevel):
        """Set minimum log level."""
        self._min_level = level

    def clear(self) -> None:
        """Clear all log entries."""
        self._entries.clear()

    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Register a callback to be notified of new log entries."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """Remove a registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _log(self, level: LogLevel, source: str, message: str) -> None:
        """Internal logging method."""
        if level < self._min_level:
            return

        entry = LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level=level.name,
            source=source,
            message=message
        )
        self._entries.append(entry)

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(entry)
            except Exception:
                pass  # Don't let callback errors break logging

    def debug(self, source: str, message: str) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, source, message)

    def info(self, source: str, message: str) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, source, message)

    def warning(self, source: str, message: str) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, source, message)

    def error(self, source: str, message: str) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, source, message)

    def save(self, filepath: Path, app_version: str = "unknown") -> Path:
        """Save log entries to a text file.

        Args:
            filepath: Path to save the log file
            app_version: Application version to include in header

        Returns:
            Path to the saved log file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Simple Scope Log - Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Application Version: {app_version}\n")
            f.write("=" * 60 + "\n\n")

            for entry in self._entries:
                f.write(str(entry) + "\n")

        return filepath

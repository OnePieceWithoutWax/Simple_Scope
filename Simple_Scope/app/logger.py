"""
Logging module for Simple Scope application using Python's built-in logging.
Provides a custom ListHandler for in-memory storage and GUI display.
"""
import logging
from datetime import datetime
from typing import Callable, List
from pathlib import Path


class ListHandler(logging.Handler):
    """Custom logging handler that stores log records in a list.

    Supports callbacks for live GUI updates and provides access to
    formatted log entries.
    """

    def __init__(self, level: int = logging.DEBUG):
        super().__init__(level)
        self._records: List[logging.LogRecord] = []
        self._callbacks: List[Callable[[logging.LogRecord], None]] = []

        # Set default formatter
        self.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)-7s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))

    @property
    def records(self) -> List[logging.LogRecord]:
        """Raw log records."""
        return self._records.copy()

    @property
    def entries(self) -> List[str]:
        """Formatted log entries as strings."""
        return [self.format(record) for record in self._records]

    def emit(self, record: logging.LogRecord) -> None:
        """Handle a log record."""
        self._records.append(record)

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(record)
            except Exception:
                pass  # Don't let callback errors break logging

    def clear(self) -> None:
        """Clear all stored log records."""
        self._records.clear()

    def add_callback(self, callback: Callable[[logging.LogRecord], None]) -> None:
        """Register a callback to be notified of new log records."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[logging.LogRecord], None]) -> None:
        """Remove a registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

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

            for entry in self.entries:
                f.write(entry + "\n")

        return filepath


def setup_logger(name: str = "SimpleScope", level: int = logging.DEBUG) -> tuple[logging.Logger, ListHandler]:
    """Create and configure a logger with ListHandler.

    Args:
        name: Logger name
        level: Minimum log level

    Returns:
        Tuple of (logger, handler) for accessing both
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    for handler in logger.handlers[:]:
        if isinstance(handler, ListHandler):
            logger.removeHandler(handler)

    handler = ListHandler(level)
    logger.addHandler(handler)

    return logger, handler

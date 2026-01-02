"""Logging utilities for the Fields application."""

import sys
import os
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels for the logger."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Logger:
    """A simple logger class for the Fields application."""

    def __init__(self, name: str = "Fields", level: LogLevel = LogLevel.INFO,
                 debug_enabled: bool = False):
        """Initialize the logger.

        Args:
            name: Name of the logger
            level: Minimum log level to output
            debug_enabled: Whether debug mode is enabled
        """
        self.name = name
        self.level = level
        self.debug_enabled = debug_enabled

    def _should_log(self, level: LogLevel) -> bool:
        """Check if a message should be logged based on the current level."""
        if self.debug_enabled:
            return level.value >= LogLevel.DEBUG.value
        return level.value >= self.level.value

    def _format_message(self, level: LogLevel, message: str) -> str:
        """Format a log message."""
        level_name = level.name.upper()
        return f"[{self.name}] {level_name}: {message}"

    def debug(self, message: str) -> None:
        """Log a debug message."""
        if self._should_log(LogLevel.DEBUG):
            formatted = self._format_message(LogLevel.DEBUG, message)
            print(formatted, file=sys.stderr)

    def info(self, message: str) -> None:
        """Log an info message."""
        if self._should_log(LogLevel.INFO):
            formatted = self._format_message(LogLevel.INFO, message)
            print(formatted)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        if self._should_log(LogLevel.WARNING):
            formatted = self._format_message(LogLevel.WARNING, message)
            print(formatted, file=sys.stderr)

    def error(self, message: str) -> None:
        """Log an error message."""
        if self._should_log(LogLevel.ERROR):
            formatted = self._format_message(LogLevel.ERROR, message)
            print(formatted, file=sys.stderr)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        if self._should_log(LogLevel.CRITICAL):
            formatted = self._format_message(LogLevel.CRITICAL, message)
            print(formatted, file=sys.stderr)

    @classmethod
    def from_debug_flag(cls, debug_enabled: bool, name: str = "Fields") -> 'Logger':
        """Create a logger instance based on debug flag.

        Args:
            debug_enabled: Whether debug mode is enabled
            name: Name of the logger

        Returns:
            Logger instance configured for the debug state
        """
        level = LogLevel.DEBUG if debug_enabled else LogLevel.INFO
        return cls(name=name, level=level, debug_enabled=debug_enabled)


# Global logger instance
_default_logger: Optional[Logger] = None


def get_logger(name: str = "Fields") -> Logger:
    """Get the default logger instance.

    Args:
        name: Name for the logger

    Returns:
        Logger instance
    """
    global _default_logger
    if _default_logger is None:
        # Check for DEBUG environment variable as fallback
        debug_enabled = os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
        _default_logger = Logger.from_debug_flag(debug_enabled, name)
    return _default_logger


def set_global_debug(debug_enabled: bool) -> None:
    """Set debug mode for the global logger.

    Args:
        debug_enabled: Whether to enable debug logging
    """
    global _default_logger
    if _default_logger is not None:
        _default_logger.debug_enabled = debug_enabled
        _default_logger.level = LogLevel.DEBUG if debug_enabled else LogLevel.INFO
    else:
        # If no logger exists yet, create one with debug enabled
        _default_logger = Logger.from_debug_flag(debug_enabled, "Fields")

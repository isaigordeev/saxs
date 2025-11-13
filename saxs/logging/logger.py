"""Logging configuration module for SAXS package.

This module provides a custom logging setup for the SAXS project,
including a PrettyLogger class that enhances log messages with
formatting and a convenient get_logger function for obtaining
configured logger instances.

The module configures basic logging with:
- INFO level by default
- Formatted output with timestamps, level, module, function, and line
- Stream handler for console output

Classes
-------
PrettyLogger
    Custom logger class that wraps messages with separators for
    better readability, especially for scheduler-related logs.

Functions
---------
get_logger(name: str) -> logging.Logger
    Returns a configured logger instance with the specified name.
"""

import logging
import sys


# Register PrettyLogger globally
class PrettyLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

    def info(self, msg, *args, **kwargs) -> None:
        # Automatically wrap messages with separators and newlines
        if "sample" in kwargs:
            sample = kwargs.pop("sample")
            msg = f"\n{'=' * 30}\n[Scheduler] {msg} on sample '{sample}'\n{'=' * 30}"
        super().info(msg, *args, **kwargs)


logging.setLoggerClass(PrettyLogger)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(module)s.%(funcName)s():%(lineno)d – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Return a PrettyLogger named after the module."""
    return logging.getLogger(name)


logger = get_logger("application logger")

"""Enhanced logging system for SAXS package.

This module provides a sophisticated, colorful, and modular logging system
for the SAXS project with component-specific formatters, visual hierarchy,
and improved readability.

Features
--------
- Colorful ANSI output with component-specific color schemes
- Component-specific loggers (Scheduler, Stage, Kernel, Pipeline)
- Visual hierarchy with icons and separators
- Context-aware formatting
- Multiple log levels with distinct styling
- Performance tracking support
- Modular logger factory pattern

Classes
-------
LogColors
    ANSI color codes for terminal output.
LogIcons
    Unicode icons for different log levels and components.
LogFormatter
    Custom formatter with color support and visual enhancements.
ComponentLogger
    Enhanced logger class with component-specific formatting.
LoggerFactory
    Factory for creating component-specific loggers.

Functions
---------
get_logger(name: str, component: str = "default") -> logging.Logger
    Returns a configured component-specific logger instance.
setup_logging(level: int = logging.INFO, enable_colors: bool = True) -> None
    Configure global logging settings.
"""

import logging
import sys
from typing import Any, ClassVar


class LogColors:
    """ANSI color codes for terminal output.

    Provides color codes for different log levels and components
    to enhance readability in terminal output.
    """

    # Reset
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright text colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @classmethod
    def strip_colors(cls, text: str) -> str:
        """Remove all ANSI color codes from text.

        Parameters
        ----------
        text : str
            Text containing ANSI codes.

        Returns
        -------
        str
            Text with all ANSI codes removed.
        """
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)


class LogIcons:
    """Unicode icons for different log levels and components.

    Provides visual indicators to quickly identify log message types
    and components.
    """

    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # Components
    SCHEDULER = "SCHEDULER"
    STAGE = "STAGE"
    KERNEL = "KERNEL"
    PIPELINE = "PIPELINE"
    DATA = "DATA"
    POLICY = "POLICY"
    CONDITION = "CONDITION"

    # Status
    START = "START"
    STOP = "STOP"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PROGRESS = "PROGRESS"
    ARROW_RIGHT = ">"
    ARROW_DOWN = "v"
    BULLET = "*"
    CHECK = "[OK]"
    CROSS = "[X]"


class LogFormatter(logging.Formatter):
    """Custom formatter with color support and visual enhancements.

    Provides colorful output with component-specific styling and
    visual hierarchy for improved readability.

    Attributes
    ----------
    enable_colors : bool
        Whether to include ANSI color codes in output.
    component : str
        Component name for specialized formatting.
    """

    # Color scheme for different log levels
    LEVEL_COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": LogColors.BRIGHT_BLACK,
        "INFO": LogColors.BRIGHT_CYAN,
        "WARNING": LogColors.BRIGHT_YELLOW,
        "ERROR": LogColors.BRIGHT_RED,
        "CRITICAL": LogColors.BG_RED + LogColors.BRIGHT_WHITE,
    }

    # Color scheme for different components
    COMPONENT_COLORS: ClassVar[dict[str, str]] = {
        "scheduler": LogColors.BRIGHT_BLUE,
        "stage": LogColors.BRIGHT_GREEN,
        "kernel": LogColors.BRIGHT_MAGENTA,
        "pipeline": LogColors.BRIGHT_CYAN,
        "data": LogColors.BRIGHT_YELLOW,
        "policy": LogColors.YELLOW,
        "condition": LogColors.CYAN,
        "default": LogColors.WHITE,
    }

    # Icons for different log levels
    LEVEL_ICONS: ClassVar[dict[str, str]] = {
        "DEBUG": LogIcons.DEBUG,
        "INFO": LogIcons.INFO,
        "WARNING": LogIcons.WARNING,
        "ERROR": LogIcons.ERROR,
        "CRITICAL": LogIcons.CRITICAL,
    }

    def __init__(
        self,
        enable_colors: bool = True,
        component: str = "default",
    ):
        """Initialize the formatter.

        Parameters
        ----------
        enable_colors : bool, optional
            Whether to enable ANSI colors (default: True).
        component : str, optional
            Component name for specialized formatting (default: "default").
        """
        super().__init__(
            fmt="%(message)s",
            datefmt="%H:%M:%S",
        )
        self.enable_colors = enable_colors
        self.component = component.lower()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and visual enhancements.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            Formatted log message with colors and styling.
        """
        if not self.enable_colors:
            return self._format_plain(record)

        return self._format_colored(record)

    def _format_colored(self, record: logging.LogRecord) -> str:
        """Format record with colors and icons.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            Colored formatted message.
        """
        # Get color schemes
        level_color = self.LEVEL_COLORS.get(
            record.levelname,
            LogColors.WHITE,
        )
        component_color = self.COMPONENT_COLORS.get(
            self.component,
            LogColors.WHITE,
        )

        # Format timestamp
        timestamp = f"{LogColors.DIM}{self.formatTime(record, self.datefmt)}{LogColors.RESET}"

        # Format level (just the abbreviated form)
        level_abbrev = {
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
        }.get(record.levelname, record.levelname[:3])

        level = f"{level_color}{level_abbrev}{LogColors.RESET}"

        # Format component (abbreviated if too long)
        component_abbrev = self.component.upper()[:8]
        component_name = (
            f"{component_color}{component_abbrev}{LogColors.RESET}"
        )

        # Format message
        message = record.getMessage()

        # Build final message with content on new line
        return f"{timestamp} {level:9s} [{component_name:14s}] {message}"

    def _format_plain(self, record: logging.LogRecord) -> str:
        """Format record without colors (plain text).

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            Plain text formatted message.
        """
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        component_name = self.component.upper()
        location = f"{record.module}.{record.funcName}():{record.lineno}"
        message = record.getMessage()

        return (
            f"{timestamp} [{level}] [{component_name}] {location} -> {message}"
        )


class ComponentLogger(logging.Logger):
    """Enhanced logger class with component-specific formatting.

    Provides specialized logging methods for different SAXS components
    with automatic context extraction and visual formatting.

    Attributes
    ----------
    component : str
        Component name for this logger instance.
    """

    def __init__(
        self,
        name: str,
        component: str = "default",
        level: int = logging.NOTSET,
    ):
        """Initialize component logger.

        Parameters
        ----------
        name : str
            Logger name.
        component : str, optional
            Component type (default: "default").
        level : int, optional
            Logging level (default: logging.NOTSET).
        """
        super().__init__(name, level)
        self.component = component

    def separator(self, char: str = "=", length: int = 80) -> None:
        """Log a visual separator line.

        Parameters
        ----------
        char : str, optional
            Character to use for separator (default: "=").
        length : int, optional
            Length of separator line (default: 80).
        """
        self.info(char * length)

    def header(self, title: str, char: str = "=", length: int = 80) -> None:
        """Log a header with title and separators.

        Parameters
        ----------
        title : str
            Header title text.
        char : str, optional
            Character for separator lines (default: "=").
        length : int, optional
            Length of separator lines (default: 80).
        """
        self.separator(char, length)
        centered = title.center(length)
        self.info(centered)
        self.separator(char, length)

    def section(self, title: str) -> None:
        """Log a section header.

        Parameters
        ----------
        title : str
            Section title.
        """
        self.info("")
        self.info(f"{LogIcons.ARROW_RIGHT} {title}")
        self.info("─" * 60)

    def step(self, step_num: int, description: str) -> None:
        """Log a numbered step.

        Parameters
        ----------
        step_num : int
            Step number.
        description : str
            Step description.
        """
        self.info(f"{LogIcons.BULLET} Step {step_num}: {description}")

    def success(self, message: str) -> None:
        """Log a success message.

        Parameters
        ----------
        message : str
            Success message.
        """
        self.info(f"[OK] {message}")

    def failure(self, message: str) -> None:
        """Log a failure message.

        Parameters
        ----------
        message : str
            Failure message.
        """
        self.error(f"[FAIL] {message}")

    def progress(self, message: str) -> None:
        """Log a progress message.

        Parameters
        ----------
        message : str
            Progress message.
        """
        self.info(f"[...] {message}")

    def stage_info(self, stage_name: str, action: str, **kwargs: Any) -> None:
        """Log stage-specific information.

        Parameters
        ----------
        stage_name : str
            Name of the stage.
        action : str
            Action being performed.
        **kwargs : Any
            Additional context information.
        """
        msg = f"[{stage_name}] {action} \n|"
        if kwargs:
            msg += "|".join(f"  {k}={v} \n" for k, v in kwargs.items())
        self.info(msg)

    def scheduler_info(
        self,
        action: str,
        queue_size: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Log scheduler-specific information.

        Parameters
        ----------
        action : str
            Scheduler action.
        queue_size : int, optional
            Current queue size.
        **kwargs : Any
            Additional context information.
        """
        msg = action
        if queue_size is not None:
            msg += f" | Queue: {queue_size}"
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            msg += f" | {context}"
        self.info(msg)

    def pipeline_info(self, action: str, **kwargs: Any) -> None:
        """Log pipeline-specific information.

        Parameters
        ----------
        action : str
            Pipeline action.
        **kwargs : Any
            Additional context information.
        """
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        msg = action
        if context:
            msg += f" | {context}"
        self.info(msg)

    def kernel_info(self, action: str, **kwargs: Any) -> None:
        """Log kernel-specific information.

        Parameters
        ----------
        action : str
            Kernel action.
        **kwargs : Any
            Additional context information.
        """
        context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        msg = action
        if context:
            msg += f" | {context}"
        self.info(msg)


class LoggerFactory:
    """Factory for creating component-specific loggers.

    Provides a centralized way to create and configure loggers
    for different SAXS components with consistent formatting.

    Attributes
    ----------
    _enable_colors : bool
        Global color enablement setting.
    _default_level : int
        Default logging level.
    _loggers : dict[str, ComponentLogger]
        Cache of created loggers.
    """

    _enable_colors: bool = True
    _default_level: int = logging.INFO
    _loggers: dict[str, ComponentLogger] = {}

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        enable_colors: bool = True,
    ) -> None:
        """Configure global logger factory settings.

        Parameters
        ----------
        level : int, optional
            Default logging level (default: logging.INFO).
        enable_colors : bool, optional
            Enable ANSI colors (default: True).
        """
        cls._default_level = level
        cls._enable_colors = enable_colors

    @classmethod
    def get_logger(
        cls,
        name: str,
        component: str = "default",
        level: int | None = None,
    ) -> ComponentLogger:
        """Get or create a component-specific logger.

        Parameters
        ----------
        name : str
            Logger name (usually __name__).
        component : str, optional
            Component type (scheduler, stage, kernel, etc.).
        level : int, optional
            Logging level (uses default if not specified).

        Returns
        -------
        ComponentLogger
            Configured component logger instance.
        """
        cache_key = f"{name}::{component}"

        if cache_key in cls._loggers:
            return cls._loggers[cache_key]

        # Create new logger
        logger = ComponentLogger(
            name,
            component=component,
            level=level or cls._default_level,
        )

        # Create and attach handler with custom formatter
        handler = logging.StreamHandler(sys.stdout)
        formatter = LogFormatter(
            enable_colors=cls._enable_colors,
            component=component,
        )
        handler.setFormatter(formatter)

        # Remove any existing handlers and add our custom one
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False

        # Cache the logger
        cls._loggers[cache_key] = logger

        return logger


# Convenience function for backwards compatibility
def get_logger(name: str, component: str = "default") -> ComponentLogger:
    """Get a component-specific logger instance.

    This is a convenience wrapper around LoggerFactory.get_logger().

    Parameters
    ----------
    name : str
        Logger name (usually __name__).
    component : str, optional
        Component type (default: "default").

    Returns
    -------
    ComponentLogger
        Configured logger instance.

    Examples
    --------
    >>> from saxs.logging.logger import get_logger
    >>> logger = get_logger(__name__, "scheduler")
    >>> logger.scheduler_info("Starting pipeline", queue_size=5)
    """
    return LoggerFactory.get_logger(name, component)


def setup_logging(
    level: int = logging.INFO,
    enable_colors: bool = True,
) -> None:
    """Configure global logging settings.

    Parameters
    ----------
    level : int, optional
        Logging level (default: logging.INFO).
    enable_colors : bool, optional
        Enable ANSI colors in output (default: True).

    Examples
    --------
    >>> from saxs.logging.logger import setup_logging
    >>> import logging
    >>> setup_logging(level=logging.DEBUG, enable_colors=True)
    """
    LoggerFactory.configure(level=level, enable_colors=enable_colors)


# Create default logger for backwards compatibility
logger = get_logger("saxs", "default")


# Component-specific logger creators
def get_scheduler_logger(name: str) -> ComponentLogger:
    """Get a scheduler-specific logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    ComponentLogger
        Scheduler logger instance.
    """
    return get_logger(name, "scheduler")


def get_stage_logger(name: str) -> ComponentLogger:
    """Get a stage-specific logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    ComponentLogger
        Stage logger instance.
    """
    return get_logger(name, "stage")


def get_kernel_logger(name: str) -> ComponentLogger:
    """Get a kernel-specific logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    ComponentLogger
        Kernel logger instance.
    """
    return get_logger(name, "kernel")


def get_pipeline_logger(name: str) -> ComponentLogger:
    """Get a pipeline-specific logger.

    Parameters
    ----------
    name : str
        Logger name.

    Returns
    -------
    ComponentLogger
        Pipeline logger instance.
    """
    return get_logger(name, "pipeline")


# Initialize with default settings
setup_logging(level=logging.INFO, enable_colors=True)

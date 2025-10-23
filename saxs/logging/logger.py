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

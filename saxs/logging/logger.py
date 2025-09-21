#
# Created by Isai GORDEEV on 20/09/2025.
#

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(module)s.%(funcName)s():%"
    "(lineno)d – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Return a logger named after the module."""
    logger = logging.getLogger(name)
    logger.propagate = True
    return logger


logger = get_logger("application logger")

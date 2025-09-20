#
# Created by Isai GORDEEV on 20/09/2025.
#

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """Return a logger named after the module."""
    return logging.getLogger(name)


logger = get_logger("application logger")

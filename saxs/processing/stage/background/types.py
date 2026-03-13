"""Background stage metadata."""

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

BACKGROUND_COEF = 0.7


@dataclass
class BackgroundStageMetadata:
    """Configuration for the Background stage."""

    background_coef: float = BACKGROUND_COEF
    background_func: Callable[..., NDArray[np.float64]] | None = None

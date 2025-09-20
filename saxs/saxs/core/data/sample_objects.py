#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


# --- Base wrapper for array-like data ---
@dataclass(frozen=True)
class BaseArrayWrapper:
    values: Optional[np.ndarray] = None

    def unwrap(self) -> Optional[np.ndarray]:
        """Return the underlying NumPy array (or None if missing)."""
        return self.values


# --- Individual type wrappers ---
@dataclass(frozen=True)
class QValues(BaseArrayWrapper):
    values: np.ndarray  # required


@dataclass(frozen=True)
class Intensity(BaseArrayWrapper):
    values: np.ndarray  # required


@dataclass(frozen=True)
class IntensityError(BaseArrayWrapper):
    values: Optional[np.ndarray] = None  # optional


@dataclass(frozen=True)
class AbstractSampleMetadata(BaseArrayWrapper):
    values: Dict[str, Any] = field(default_factory=dict)

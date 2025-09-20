#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np


# --- Base wrapper for array-like data ---
@dataclass(frozen=True)
class BaseDataType:
    values: Optional[Any] = None

    def unwrap(self) -> Optional[Any]:
        """Return the underlying NumPy array (or None if missing)."""
        return self.values


# --- Individual type wrappers ---
@dataclass(frozen=True)
class QValues(BaseDataType):
    values: np.ndarray  # required


@dataclass(frozen=True)
class Intensity(BaseDataType):
    values: np.ndarray  # required


@dataclass(frozen=True)
class IntensityError(BaseDataType):
    values: Optional[np.ndarray] = None  # optional


@dataclass(frozen=True)
class AbstractSampleMetadata(BaseDataType):
    values: Dict[str, Any] = field(default_factory=dict)

#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

from saxs.algo.data.abstract_data import AData


# --- Individual type wrappers ---
@dataclass(frozen=True)
class QValues:
    values: np.ndarray


@dataclass(frozen=True)
class Intensity:
    values: np.ndarray


@dataclass(frozen=True)
class IntensityError:
    values: Optional[np.ndarray] = None


@dataclass(frozen=True)
class AbstractSampleMetadata(AData):
    data: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        return f"Stage metadata with keys: {list(self.data.keys())}"

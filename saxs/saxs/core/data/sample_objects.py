#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np

from saxs.saxs.core.data.abstract_data import BaseDataType


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

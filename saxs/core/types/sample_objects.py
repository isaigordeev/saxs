"""Sample data type aliases (simplified).

Re-exports from the new locations for backwards compatibility.
"""

from saxs.core.types.abstract_data import (
    Intensity,
    IntensityError,
    QValues,
)
from saxs.core.types.sample import SampleMetadata

__all__ = [
    "Intensity",
    "IntensityError",
    "QValues",
    "SampleMetadata",
]

"""Base data type aliases for SAXS pipeline.

Provides type aliases for SAXS array data.
"""

import numpy as np
from numpy.typing import NDArray

# Type aliases for SAXS array data
QValues = NDArray[np.float64]
Intensity = NDArray[np.float64]
IntensityError = NDArray[np.float64]

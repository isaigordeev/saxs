"""SAXS sample and metadata types.

Simple dataclass-based types for SAXS data.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from saxs.core.types.abstract_data import Intensity, IntensityError, QValues


@dataclass
class SampleMetadata:
    """Metadata associated with a SAXS sample."""

    current_peak: int | None = None
    unprocessed_peaks: dict[int, np.float64] = field(default_factory=dict)
    processed_peaks: dict[int, np.float64] = field(default_factory=dict)


@dataclass
class SAXSSample:
    """Represents a Small-Angle X-ray Scattering sample.

    Attributes
    ----------
    q_values : NDArray[np.float64]
        Scattering vector magnitudes.
    intensity : NDArray[np.float64]
        Measured scattering intensities.
    intensity_err : NDArray[np.float64]
        Measurement errors for intensities.
    metadata : SampleMetadata
        Associated sample metadata.
    """

    q_values: QValues
    intensity: Intensity
    intensity_err: IntensityError
    metadata: SampleMetadata = field(default_factory=SampleMetadata)

"""SAXS core types.

Provides type aliases, sample, and metadata dataclasses for the SAXS pipeline.
"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

# Type aliases for SAXS array data
QValues = NDArray[np.float64]
Intensity = NDArray[np.float64]
IntensityError = NDArray[np.float64]


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


@dataclass
class FlowMetadata:
    """Metadata flowing between pipeline stages.

    Attributes
    ----------
    sample : str
        Sample name/identifier.
    processed_peaks : dict[int, float]
        Peaks that have been processed (index -> intensity).
    unprocessed_peaks : dict[int, float]
        Peaks awaiting processing (index -> intensity).
    current_peak : int | None
        Index of the peak currently being processed.
    """

    sample: str = ""
    processed_peaks: dict[int, np.float64] = field(default_factory=dict)
    unprocessed_peaks: dict[int, np.float64] = field(default_factory=dict)
    current_peak: int | None = None


@dataclass
class SchedulerMetadata:
    """Metadata for scheduler operations."""

    processed_count: int = 0
    peaks: set[int] = field(default_factory=set)


__all__ = [
    "FlowMetadata",
    "Intensity",
    "IntensityError",
    "QValues",
    "SAXSSample",
    "SampleMetadata",
    "SchedulerMetadata",
]

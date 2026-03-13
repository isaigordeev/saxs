"""Flow metadata for inter-stage communication."""

from dataclasses import dataclass, field

import numpy as np


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

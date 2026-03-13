"""Peak processing stage metadata."""

from dataclasses import dataclass


@dataclass
class PeakFindStageMetadata:
    """Configuration for the FindPeak stage."""

    height: float = 0.5
    prominence: float = 0.3
    distance: int = 10


@dataclass
class ProcessPeakStageMetadata:
    """Configuration for the ProcessPeak stage."""

    fit_range: int = 2


DEFAULT_PEAK_FIND_META = PeakFindStageMetadata()
DEFAULT_PEAK_PROCESS_META = ProcessPeakStageMetadata()

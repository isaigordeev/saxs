"""Processing stages for SAXS data pipeline."""

from saxs.processing.stages.background import (
    BACKGROUND_COEF,
    BackgroundStage,
    BackgroundStageMetadata,
)
from saxs.processing.stages.cut import CutStage, CutStageMetadata
from saxs.processing.stages.filter import FilterStage
from saxs.processing.stages.peak import (
    DEFAULT_PEAK_FIND_META,
    DEFAULT_PEAK_PROCESS_META,
    FindPeakStage,
    PeakFindStageMetadata,
    ProcessPeakStage,
    ProcessPeakStageMetadata,
)

__all__ = [
    "BACKGROUND_COEF",
    "BackgroundStage",
    "BackgroundStageMetadata",
    "CutStage",
    "CutStageMetadata",
    "DEFAULT_PEAK_FIND_META",
    "DEFAULT_PEAK_PROCESS_META",
    "FilterStage",
    "FindPeakStage",
    "PeakFindStageMetadata",
    "ProcessPeakStage",
    "ProcessPeakStageMetadata",
]

"""Processing stages for SAXS data pipeline."""

from saxs.processing.stage.background.background import BackgroundStage
from saxs.processing.stage.background.types import (
    BACKGROUND_COEF,
    BackgroundStageMetadata,
)
from saxs.processing.stage.cut.cut import CutStage
from saxs.processing.stage.cut.types import CutStageMetadata
from saxs.processing.stage.filter.filter import FilterStage
from saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.processing.stage.peak.process_peak import ProcessPeakStage
from saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    DEFAULT_PEAK_PROCESS_META,
    PeakFindStageMetadata,
    ProcessPeakStageMetadata,
)

__all__ = [
    "BackgroundStage",
    "BackgroundStageMetadata",
    "BACKGROUND_COEF",
    "CutStage",
    "CutStageMetadata",
    "FilterStage",
    "FindPeakStage",
    "PeakFindStageMetadata",
    "DEFAULT_PEAK_FIND_META",
    "ProcessPeakStage",
    "ProcessPeakStageMetadata",
    "DEFAULT_PEAK_PROCESS_META",
]

"""Cut stage metadata."""

from dataclasses import dataclass

DEFAULT_CUT_POINT = 100


@dataclass
class CutStageMetadata:
    """Configuration for the Cut stage."""

    cut_point: int = DEFAULT_CUT_POINT

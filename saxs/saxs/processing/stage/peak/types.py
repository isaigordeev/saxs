from dataclasses import field

from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)
from saxs.saxs.core.types.stage_metadata import (
    TAbstractStageMetadata,
)


class EPeakFindMetadataKeys(EMetadataSchemaKeys):
    """Enum of keys used in PeakFindStageMetadataDict."""

    HEIGHT = "height"
    PROMINENCE = "prominence"
    DISTANCE = "distance"


class PeakFindStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """

    height: float
    prominence: float
    distance: int


DEFAULT_PEAK_FIND_DICT = PeakFindStageMetadataDict(
    {
        EPeakFindMetadataKeys.PROMINENCE.value: 0.3,
        EPeakFindMetadataKeys.HEIGHT.value: 0.5,
        EPeakFindMetadataKeys.DISTANCE.value: 10,
    },
)


class PeakFindStageMetadata(
    TAbstractStageMetadata[PeakFindStageMetadataDict, EPeakFindMetadataKeys],
):
    """
    Metadata object representing the PeakFind stage configuration.

    Attributes
    ----------
    value : CutStageMetadataDict
        Underlying metadata dictionary, defaulting to
        `{"cut_point": 0}`.
    """

    Keys = EPeakFindMetadataKeys
    Dict = PeakFindStageMetadataDict

    value: PeakFindStageMetadataDict = field(
        default_factory=lambda: DEFAULT_PEAK_FIND_DICT,
    )


DEFAULT_PEAK_FIND_META = PeakFindStageMetadata(DEFAULT_PEAK_FIND_DICT)


class EPeakProcessMetadataKeys(EMetadataSchemaKeys):
    """Enum of keys used in PeakFindStageMetadataDict."""

    CURRENT_PEAK = "current_peak"


class PeakProcessStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """

    current_peak: int


class ProcessPeakStageMetadata(
    TAbstractStageMetadata[
        PeakProcessStageMetadataDict,
        EPeakProcessMetadataKeys,
    ],
):
    """
    Metadata object representing the Cut stage configuration.

    Provides a builder-style, type-safe interface around
    a `CutStageMetadataDict` dictionary, with convenient
    accessors and default initialization.

    Attributes
    ----------
    value : CutStageMetadataDict
        Underlying metadata dictionary, defaulting to
        `{"cut_point": 0}`.
    """

    Keys = EPeakProcessMetadataKeys
    Dict = PeakProcessStageMetadataDict

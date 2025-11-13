"""Peak processing stage metadata types.

This module defines the metadata types and default configurations
for peak finding and processing stages in the SAXS pipeline.

It provides:
- Enumeration of metadata keys for peak finding (height, prominence,
  distance)
- Enumeration of metadata keys for peak processing (fit_range)
- Typed dictionaries for stage metadata schemas
- Default metadata instances for both peak finding and processing
  stages

Classes
-------
EPeakFindMetadataKeys
    Enumeration of keys used in peak finding stage metadata.
EPeakProcessMetadataKeys
    Enumeration of keys used in peak processing stage metadata.
PeakFindStageMetadataDict
    Typed dictionary schema for peak finding stage metadata.
PeakProcessStageMetadataDict
    Typed dictionary schema for peak processing stage metadata.
PeakFindStageMetadata
    Metadata object for peak finding stage configuration.
ProcessPeakStageMetadata
    Metadata object for peak processing stage configuration.
"""

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

    FIT_RANGE = "fit_range"


class PeakProcessStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """

    fit_range: int


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


DEFAULT_PEAK_PROCESS_DICT = PeakProcessStageMetadataDict(
    {
        EPeakProcessMetadataKeys.FIT_RANGE.value: 2,
    },
)

DEFAULT_PEAK_PROCESS_META = ProcessPeakStageMetadata(DEFAULT_PEAK_PROCESS_DICT)

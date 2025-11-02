from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)
from saxs.saxs.core.types.stage_metadata import (
    TAbstractStageMetadata,
)


class EPeakFindMetadataKeys(EMetadataSchemaKeys):
    """Enum of keys used in PeakFindStageMetadataDict."""


class PeakFindStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """


class PeakFindStageMetadata(TAbstractStageMetadata[PeakFindStageMetadataDict]):
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

    value: PeakFindStageMetadataDict = field(
        default_factory=lambda: {
            EBackMetadataKeys.PeakFind_COEF.value: 0.3,
        },
    )

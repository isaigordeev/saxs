"""
Module: saxs_cut_stage_metadata.

Defines metadata structures for the SAXS "Cut" stage.

This module provides a TypedDict-based schema and a corresponding
metadata wrapper class (`CutStageMetadata`) for representing
metadata associated with a SAXS data processing "Cut" stage.
The "Cut" stage typically defines a single integer cut point in
the dataset, representing the index or q-value position at which
data should be truncated or split.

Classes
-------
CutStageMetadataDictKeys : Enum
    Enumeration of valid keys for the CutStage metadata dictionary.
CutStageMetadataDict : TypedDict
    TypedDict schema specifying the allowed metadata fields.
CutStageMetadata : AbstractStageMetadata
    Concrete metadata class with convenience accessors and defaults.
"""

from dataclasses import field

from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


class ECutStageMetadataDictKeys(EMetadataSchemaKeys):
    """Enum of keys used in CutStageMetadataDict."""

    CUT_POINT = "cut_point"


class CutStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """

    cut_point: int


class CutStageMetadata(TAbstractStageMetadata[CutStageMetadataDict]):
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

    value: CutStageMetadataDict = field(
        default_factory=lambda: {ECutStageMetadataDictKeys.CUT_POINT.value: 0},
    )

    def get_cut_point(self) -> int:
        """
        Return the configured cut point.

        Returns
        -------
        int
            The cut point index from metadata, defaulting to 0
            if not set.
        """
        return self.unwrap().get(ECutStageMetadataDictKeys.CUT_POINT.value, 0)

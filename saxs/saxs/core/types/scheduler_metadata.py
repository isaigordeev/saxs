"""
Scheduler metadata module.

This module defines types and classes for managing metadata
associated with a stage scheduler in SAXS processing. It provides:

- `ESchedulerMetadataDictKeys`: Enum for valid metadata keys in
   scheduler context.
- `SchedulerMetadataDict`: Typed dictionary for scheduler metadata.
- `AbstractSchedulerMetadata`: Dict-like container for scheduler
   metadata
  supporting default values and human-readable descriptions.

The metadata system is built on top of `AbstractMetadata`, allowing
immutable-style updates while still providing familiar dictionary
interfaces for access and assignment.
"""


# Created by Isai Gordeev on 22/09/2025.

from dataclasses import field
from enum import Enum

from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
    TAbstractMetadata,
)


class ESchedulerRuntime(Enum):
    """Enum for runtime constants."""

    UNDEFINED_PEAK = -1


class ESchedulerMetadataDictKeys(EMetadataSchemaKeys):
    """
    Enumeration of keys for scheduler metadata.

    Attributes
    ----------
    PROCESSED : str
        Counter for the number of processed items.
    PEAKS : str
        Set of detected peaks.
    """

    PROCESSED = "processed_peaks"
    PEAKS = "peaks"


class SchedulerMetadataDict(MetadataSchemaDict, total=False):
    """
    Typed dictionary for scheduler-specific metadata.

    This dictionary may contain:

    Attributes
    ----------
    processed : int, optional
        Counter for processed items. Defaults to 0.
    peaks : set[int], optional
        Set of detected peak indices.
    """

    processed_peaks: int
    peaks: set[int]


class SchedulerMetadata(
    TAbstractMetadata[
        SchedulerMetadataDict,
        ESchedulerMetadataDictKeys,
    ],
):
    """
    Metadata container for stage scheduler operations.

    Inherits from AbstractMetadata to provide dict-like access
    to scheduler-specific metadata keys.

    Attributes
    ----------
    value : SchedulerMetadataDict
        Default metadata dictionary with initial values.
        By default, the 'processed' counter is set to 0.

    Methods
    -------
    describe()
        Return a human-readable string describing the metadata keys.
    """

    Keys = ESchedulerMetadataDictKeys
    Dict = SchedulerMetadataDict

    value: SchedulerMetadataDict = field(
        default_factory=lambda: {
            ESchedulerMetadataDictKeys.PROCESSED.value: 0,
        },
    )

    def describe(self) -> str:
        """
        Generate a string description of the scheduler metadata.

        Returns
        -------
        str
            Description listing the metadata keys available
            in this instance.
        """
        return f"Stage scheduler metadata with keys: {list(self.value.keys())}"

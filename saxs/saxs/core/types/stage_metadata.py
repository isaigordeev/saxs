"""
Module: stage_metadata.

This module defines the `AbstractStageMetadata` class — a
lightweight, immutable wrapper for stage-level metadata within the
SAXS pipeline.

Stage metadata objects store contextual information about a pipeline
stage (e.g., configuration parameters, labels, dependencies, or
timestamps) and are designed for safe, type-consistent propagation
between processing components.
"""

from typing import TypedDict, TypeVar

from saxs.saxs.core.types.metadata import AbstractMetadata


class StageSchemaDict(TypedDict, total=False):
    """Abstract dictionary schema."""


TStageMetadataDict = TypeVar("TStageMetadataDict", bound=StageSchemaDict)


class TAbstractStageMetadata(AbstractMetadata[TStageMetadataDict]):
    """
    Represents metadata associated with a SAXS pipeline stage.

    This class provides an immutable container for structured
    metadata used during stage configuration, scheduling, or
    execution. It ensures a consistent type (`dict[str, Any]`) for
    all stage metadata throughout the pipeline.

    Example:
        >>> metadata = AbstractStageMetadata(values={
        ...     "stage_name": "Normalization",
        ...     "version": "1.2.0",
        ... })
        >>> metadata.unwrap()["stage_name"]
        'Normalization'

    Attributes
    ----------
        values (dict[str, Any]): A dictionary of stage metadata
            entries, such as configuration options, stage
            identifiers, or notes.  Defaults to an empty dictionary
            if not provided.
    """

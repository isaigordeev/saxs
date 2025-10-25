"""
Module: flow_metadata.

This module defines the data structures used to store metadata for
flow experiments. It includes a TypedDict for type-safe metadata
keys and a frozen dataclass to wrap the metadata in an immutable
container.
"""

from dataclasses import dataclass, field
from typing import TypedDict

from saxs.saxs.core.types.abstract_data import BaseDataType


class FlowMetadataDict(TypedDict, total=False):
    """
    Type-safe dictionary for flow metadata.

    Keys:
        sample_name (str, optional): The name of the sample.
        peaks (list[int], optional): List of peak positions detected
        in the experiment.
    """

    sample_name: str
    peaks: list[int]


@dataclass(frozen=False)
class FlowMetadata(BaseDataType):
    """
    Immutable container for flow experiment metadata.

    Attributes
    ----------
        values (FlowMetadataDict): Metadata values for a flow
        experiment. Uses a TypedDict to provide type hints and
        optional keys.
    """

    values: FlowMetadataDict = field(default=FlowMetadataDict())

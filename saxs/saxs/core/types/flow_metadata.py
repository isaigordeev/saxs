"""flow_metadata.py.

Module for flowing metadata.
"""

from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
    TAbstractMetadata,
)


class FlowMetadataDict(MetadataSchemaDict, total=False):
    """
    Type-safe dictionary for flow metadata.

    Keys:
        sample_name (str, optional): The name of the sample.
        peaks (list[int], optional): List of peak positions detected
        in the experiment.
    """

    sample: str
    processed_peaks: set[int]
    unprocessed_peaks: set[int]
    current: int


class FlowMetadataKeys(EMetadataSchemaKeys):
    """Flow metadata keys which are possibly passed."""

    SAMPLE = "sample"
    PROCESSED = "processed_peaks"
    UNPROCESSED = "unprocessed_peaks"
    CURRENT = "current"


class FlowMetadata(TAbstractMetadata[FlowMetadataDict, FlowMetadataKeys]):
    """
    Immutable container for flow experiment metadata.

    Attributes
    ----------
        values (FlowMetadataDict): Metadata values for a flow
        experiment. Uses a TypedDict to provide type hints and
        optional keys.
    """

    Keys: type[FlowMetadataKeys] = FlowMetadataKeys
    Dict: type[FlowMetadataDict] = FlowMetadataDict

    value: FlowMetadataDict

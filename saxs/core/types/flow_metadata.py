"""flow_metadata.py.

Module for flowing metadata.
"""

import numpy as np

from saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
    TAbstractMetadata,
)
from saxs.core.types.scheduler_metadata import ERuntimeConstants


class FlowMetadataDict(MetadataSchemaDict, total=False):
    """
    Type-safe dictionary for flow metadata.

    Keys:
        sample_name (str, optional): The name of the sample.
        peaks (list[int], optional): List of peak positions detected
        in the experiment.
    """

    sample: str
    processed_peaks: dict[int, np.float64]
    unprocessed_peaks: dict[int, np.float64] | ERuntimeConstants
    current: dict[int, np.float64] | ERuntimeConstants  # simplify


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

from saxs.saxs.core.types.metadata import AbstractMetadata, MetadataSchemaDict


class FlowMetadataDict(MetadataSchemaDict, total=False):
    """
    Type-safe dictionary for flow metadata.

    Keys:
        sample_name (str, optional): The name of the sample.
        peaks (list[int], optional): List of peak positions detected
        in the experiment.
    """

    sample_name: str


class FlowMetadata(AbstractMetadata[FlowMetadataDict]):
    """
    Immutable container for flow experiment metadata.

    Attributes
    ----------
        values (FlowMetadataDict): Metadata values for a flow
        experiment. Uses a TypedDict to provide type hints and
        optional keys.
    """

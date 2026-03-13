"""Stage request types."""

from dataclasses import dataclass

from saxs.core.types.flow_metadata import FlowMetadata


@dataclass
class IAbstractStageRequest:
    """Base class for stage addition requests."""


@dataclass
class StageRequest(IAbstractStageRequest):
    """Request for adding a new stage to the pipeline.

    Attributes
    ----------
    condition_eval_metadata : FlowMetadata
        Metadata used to evaluate the chaining condition.
    flow_metadata : FlowMetadata
        Metadata passed to the next stage.
    """

    condition_eval_metadata: FlowMetadata
    flow_metadata: FlowMetadata

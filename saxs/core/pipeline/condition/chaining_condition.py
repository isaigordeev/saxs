"""Chaining condition: checks if there are remaining peaks."""

from saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.core.types.flow_metadata import FlowMetadata


class ChainingPeakCondition(StageCondition):
    """True if there is a current peak to process."""

    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        return eval_metadata.current_peak is not None

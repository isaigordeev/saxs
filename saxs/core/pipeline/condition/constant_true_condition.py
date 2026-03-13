"""Always-true condition."""

from saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.core.types.flow_metadata import FlowMetadata


class TrueCondition(StageCondition):
    """Condition that always passes."""

    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        _ = eval_metadata
        return True

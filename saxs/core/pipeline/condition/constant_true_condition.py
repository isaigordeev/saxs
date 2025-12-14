"""Module with primitive predicat."""


# Created by Isai Gordeev on 20/09/2025.

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.stage.request.abst_request import EvalMetadata


class TrueCondition(StageCondition):
    """True condition for a pending stage.

    True condition for a stage to be added by a conditional stage.
    """

    def evaluate(self, eval_metadata: EvalMetadata) -> bool:
        """Primitive predicat."""
        _ = eval_metadata
        return True

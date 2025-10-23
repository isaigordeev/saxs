#
# Created by Isai GORDEEV on 22/09/2025.
#

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class TrueCondition(StageCondition):
    def evaluate(self, metadata: AbstractStageMetadata) -> bool:  # noqa: ARG002
        return True

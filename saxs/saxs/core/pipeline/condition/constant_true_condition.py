# Created by Isai Gordeev on 20/09/2025.

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


class TrueCondition(StageCondition):
    def evaluate(self, metadata: TAbstractStageMetadata) -> bool:  # noqa: ARG002
        return True

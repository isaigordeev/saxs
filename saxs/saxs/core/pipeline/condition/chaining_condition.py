#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class ChainingPeakCondition(StageCondition):
    def __init__(self, key: str):
        self.key = key

    def evaluate(self, eval_metadata: AbstractStageMetadata) -> bool:
        return len(eval_metadata.unwrap().get(self.key)) > 0

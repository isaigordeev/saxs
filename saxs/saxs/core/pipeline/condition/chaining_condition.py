# Created by Isai Gordeev on 20/09/2025.

from typing import Any
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


class ChainingPeakCondition(StageCondition):
    def __init__(self, key: str):
        self.key = key

    def evaluate(self, eval_metadata: TAbstractStageMetadata[Any]) -> bool:
        return len(eval_metadata.unwrap().get(self.key)) > 0

#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.types.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)


class ChainingPeakCondition(StageCondition):
    def __init__(self, key: str):
        self.key = key

    def evaluate(self, metadata: AbstractSampleMetadata) -> bool:
        return len(metadata.unwrap().get(self.key)) > 0

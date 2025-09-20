#
# Created by Isai GORDEEV on 19/09/2025.
#

from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    AbstractCondition,
)


class ThresholdCondition(AbstractCondition):
    def __init__(self, key: str, threshold: float):
        self.key = key
        self.threshold = threshold

    def evaluate(self, sample: AbstractSampleMetadata) -> bool:
        value = sample.metadata.get(self.key, 0)
        return value > self.threshold

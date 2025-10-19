#
# Created by Isai GORDEEV on 19/09/2025.
#

from saxs.saxs.core.types.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)


class ThresholdCondition(SampleCondition):
    def __init__(self, key: str, threshold: float):
        self.key = key
        self.threshold = threshold

    def evaluate(self, metadata: AbstractSampleMetadata) -> bool:
        value = metadata.unwrap().get(self.key, 0)
        return value > self.threshold

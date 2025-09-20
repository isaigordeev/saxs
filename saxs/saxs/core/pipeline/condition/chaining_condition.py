#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)


class ChainingPeakCondition(SampleCondition):
    def __init__(self, key: str, expected_value):
        self.key = key
        self.expected_value = expected_value

    def evaluate(self, sample: AbstractSampleMetadata) -> bool:
        return sample.metadata.get(self.key) == self.expected_value

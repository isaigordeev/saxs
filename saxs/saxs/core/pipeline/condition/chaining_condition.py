#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)


class ChainingPeakCondition(SampleCondition):
    def __init__(self, key: str):
        self.key = key

    def evaluate(self, metadata: AbstractSampleMetadata) -> bool:
        return bool(metadata.unwrap().get(self.key))

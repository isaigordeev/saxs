#
# Created by Isai GORDEEV on 19/09/2025.
#

from saxs.algo.data.sample_objects import AbstractSampleMetadata
from saxs.algo.pipeline.condition.abstract_condition import AbstractCondition


class MetadataCondition(AbstractCondition):
    def __init__(self, key: str, expected_value):
        self.key = key
        self.expected_value = expected_value

    def evaluate(self, sample: AbstractSampleMetadata) -> bool:
        return sample.metadata.get(self.key) == self.expected_value

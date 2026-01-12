# Created by Isai Gordeev on 20/09/2025.

from saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)
from saxs.core.types.sample_objects import SampleMetadata


class MetadataCondition(SampleCondition):
    def __init__(self, key: str, expected_value):
        self.key = key
        self.expected_value = expected_value

    def evaluate(self, metadata: SampleMetadata) -> bool:
        return metadata.unwrap().get(self.key) == self.expected_value

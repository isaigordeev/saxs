"""Metadata equality condition."""

from saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.core.types.sample import SampleMetadata


class MetadataCondition(SampleCondition):
    """True if a metadata value matches an expected value."""

    def __init__(self, key: str, expected_value):
        self.key = key
        self.expected_value = expected_value

    def evaluate(self, metadata: SampleMetadata) -> bool:
        return getattr(metadata, self.key, None) == self.expected_value

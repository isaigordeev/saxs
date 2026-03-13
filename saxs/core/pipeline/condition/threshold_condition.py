"""Threshold-based condition."""

from saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.core.types.sample import SampleMetadata


class ThresholdCondition(SampleCondition):
    """True if a metadata value exceeds a threshold."""

    def __init__(self, key: str, threshold: float):
        self.key = key
        self.threshold = threshold

    def evaluate(self, metadata: SampleMetadata) -> bool:
        value = getattr(metadata, self.key, 0)
        return value > self.threshold

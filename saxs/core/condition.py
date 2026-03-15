"""Condition classes for stage chaining and sample evaluation."""

from saxs.core.stage import SampleCondition, StageCondition
from saxs.core.types import FlowMetadata, SampleMetadata


class ChainingPeakCondition(StageCondition):
    """True if there is a current peak to process."""

    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        return eval_metadata.current_peak is not None


class TrueCondition(StageCondition):
    """Condition that always passes."""

    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        _ = eval_metadata
        return True


class ThresholdCondition(SampleCondition):
    """True if a metadata value exceeds a threshold."""

    def __init__(self, key: str, threshold: float):
        self.key = key
        self.threshold = threshold

    def evaluate(self, metadata: SampleMetadata) -> bool:
        value = getattr(metadata, self.key, 0)
        return value > self.threshold


class MetadataCondition(SampleCondition):
    """True if a metadata value matches an expected value."""

    def __init__(self, key: str, expected_value):
        self.key = key
        self.expected_value = expected_value

    def evaluate(self, metadata: SampleMetadata) -> bool:
        return getattr(metadata, self.key, None) == self.expected_value


__all__ = [
    "ChainingPeakCondition",
    "MetadataCondition",
    "ThresholdCondition",
    "TrueCondition",
]

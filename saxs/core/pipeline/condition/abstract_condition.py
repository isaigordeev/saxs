"""Abstract condition classes."""

from abc import ABC, abstractmethod

from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SampleMetadata


class SampleCondition(ABC):
    """Condition evaluated against sample metadata."""

    @abstractmethod
    def evaluate(self, eval_metadata: SampleMetadata) -> bool:
        """Return True if the condition passes."""


class StageCondition(ABC):
    """Condition evaluated against flow metadata for stage chaining."""

    @abstractmethod
    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        """Return True if the condition passes."""

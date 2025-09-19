from abc import ABC, abstractmethod

from saxs.algo.data.sample_objects import AbstractSampleMetadata


class SampleCondition(ABC):
    @abstractmethod
    def evaluate(self, sample: AbstractSampleMetadata) -> bool:
        """Return True if the condition passes for the given sample."""
        pass

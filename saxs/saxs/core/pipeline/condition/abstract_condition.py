from abc import ABC, abstractmethod

from saxs.saxs.core.types.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class SampleCondition(ABC):
    @abstractmethod
    def evaluate(self, eval_metadata: AbstractSampleMetadata) -> bool:
        """Predicat for sample approval.

        Return True if the condition passes for
        the given sample.
        """


class StageCondition(ABC):
    @abstractmethod
    def evaluate(self, eval_metadata: AbstractStageMetadata) -> bool:
        """Predicat for stage approval.

        Return True if the condition passes for the
        given stage metadata.
        """

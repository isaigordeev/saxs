from abc import ABC, abstractmethod

from saxs.saxs.core.stage.request.abst_request import EvalMetadata
from saxs.saxs.core.types.sample_objects import SampleMetadata


class SampleCondition(ABC):
    @abstractmethod
    def evaluate(self, eval_metadata: SampleMetadata) -> bool:
        """Predicat for sample approval.

        Return True if the condition passes for
        the given sample.
        """


class StageCondition(ABC):
    @abstractmethod
    def evaluate(self, eval_metadata: EvalMetadata) -> bool:
        """Predicat for stage approval.

        Return True if the condition passes for the
        given stage metadata.
        """

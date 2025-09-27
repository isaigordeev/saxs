from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Type, Union

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.stage.abstract_cond_stage import AbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.request.abst_request import StageRequest


class AbstractKernel(ABC):
    @abstractmethod
    def create_sample(self, *args, **kwargs) -> "SAXSSample":
        """Factory for building a sample."""
        pass

    @abstractmethod
    def define_pipeline(
        self,
    ) -> List[Any]:
        """Define which stages and policies form the entrypoint pipeline."""
        pass

    def build_pipeline(self):
        """Build entry stages and submit them to scheduler."""
        raise NotImplementedError()

    def run(self, init_sample: "SAXSSample"):
        """Run the scheduler until pipeline is complete."""
        raise NotImplementedError()

    @staticmethod
    def build_initial_stage(*args, **kwargs):
        raise NotImplementedError()

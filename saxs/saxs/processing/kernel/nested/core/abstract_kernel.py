from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Union

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
    ) -> List[
        Union[
            Type["AbstractStage"],
            Tuple[Type["AbstractRequestingStage"], "ChainingPolicy"],
        ]
    ]:
        """Define which stages and policies form the entrypoint pipeline."""
        pass

    def build_pipeline(self):
        """Build entry stages and submit them to scheduler."""
        stage_defs = self.define_pipeline()
        initial_stages = self.build_initial_stages(stage_defs, self.registry)

        self.pipeline = Pipeline.with_stages(
            *initial_stages,
            scheduler=self.scheduler,
            scheduler_policy=self.scheduler_policy,
        )

    def run(self, init_sample: "SAXSSample"):
        """Run the scheduler until pipeline is complete."""
        return self.pipeline.run(init_sample)

    @staticmethod
    def build_initial_stage():
        raise NotImplementedError()

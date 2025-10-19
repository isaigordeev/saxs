from abc import abstractmethod
from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    InsertionPolicy,
    SaturationInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import AbstractScheduler
from saxs.saxs.core.stage.abstract_cond_stage import AbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.policy.policy_registry import PolicyRegistry
from saxs.saxs.core.kernel.spec.core.abstract_decl_kernel import (
    AbstractKernelSpec,
)

from typing import Any, Dict, List, Tuple, Type, Union


class BaseKernel(AbstractKernelSpec):
    """
    Encapsulates orchestration of:
    - pipeline building
    - scheduler wiring
    - sample creation
    """

    def __init__(
        self,
        scheduler: "AbstractScheduler",
        scheduler_policy: InsertionPolicy,
    ):
        self.scheduler = scheduler
        self.registry = PolicyRegistry()
        self.scheduler_policy = scheduler_policy or SaturationInsertPolicy()

    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    @staticmethod
    def build_initial_stages(order: list[str]) -> List["AbstractStage"]:
        """
        Build all initial stages with optional kwargs and logging.
        """
        stages = []

        logger.info(f"Total stages built: {len(stages)}")
        return stages

    def build(self):
        """Build entry stages and submit them to scheduler."""
        stage_defs = self.define()
        initial_stages = self.build_initial_stages(stage_defs, self.registry)

        self.pipeline = Pipeline.with_stages(
            *initial_stages,
            scheduler=self.scheduler,
            scheduler_policy=self.scheduler_policy,
        )

    def run(self, init_sample):
        """Run the scheduler until pipeline is complete."""
        return self.pipeline.run(init_sample)

    @abstractmethod
    def define(
        self,
    ) -> List[
        Union[
            Type["AbstractStage"],
            Tuple[Type["AbstractRequestingStage"], "ChainingPolicy"],
        ]
    ]:
        """Define which stages and policies form the entrypoint pipeline."""
        pass

from abc import abstractmethod
from typing import Any, Dict, List, Tuple, Type, Union

from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.kernel.forward.core.abstract_kernel import (
    AbstractKernel,
)
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


class BaseKernel(AbstractKernel):
    """
    Base kernel class.

    Encapsulates orchestration of:
    - pipeline building
    - scheduler wiring
    - sample creation.
    """

    def __init__(
        self,
        scheduler: "AbstractScheduler",
        scheduler_policy: InsertionPolicy,
    ):
        self.scheduler = scheduler
        self.registry = PolicyRegistry()
        self.scheduler_policy = scheduler_policy or SaturationInsertPolicy()

    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""
        stage_defs = self.define()
        initial_stages = self.build_initial_stages(stage_defs, self.registry)

        self.pipeline = Pipeline.with_stages(
            *initial_stages,
            scheduler=self.scheduler,
            scheduler_policy=self.scheduler_policy,
        )

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the scheduler until pipeline is complete."""
        return self.pipeline.run(init_sample)

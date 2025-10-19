from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.kernel_compiler import BaseCompiler
from saxs.saxs.core.kernel.spec.core.abstract_kernel import (
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
        self.scheduler_policy = scheduler_policy or SaturationInsertPolicy()
        self.execution_order: list[str] = []

    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""
        _stage_decl, _policy_decl, _execution_order = self.define()

        _comp = BaseCompiler()

        self.stage_buffer: Buffer[AbstractStage]
        self.policy_buffer: Buffer[ChainingPolicy]

        self.stage_buffer, self.policy_buffer = _comp.build(
            _stage_decl,
            _policy_decl,
        )

        _initial_stages = self._get_initial_stage(_execution_order)

        self.pipeline = Pipeline.with_stages(
            _initial_stages,
            scheduler=self.scheduler,
            scheduler_policy=self.scheduler_policy,
        )

    def _get_initial_stage(
        self,
        _execution_order: list[str],
    ) -> list[AbstractStage]:
        _initial_stages: list[AbstractStage] = []

        for _stage_id in _execution_order:
            _stage = self.stage_buffer.get(_stage_id)
            if _stage:
                _initial_stages.append(_stage)

        return _initial_stages

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the scheduler until pipeline is complete."""
        return self.pipeline.run(init_sample)

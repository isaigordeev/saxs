"""
base_kernel.py.

This module defines the `BaseKernel` class, which implements the
core execution orchestration for SAXS (Small-Angle X-ray Scattering)
pipelines. The kernel coordinates the pipeline build process,
scheduler integration, and initial sample processing.

The `BaseKernel` serves as a high-level orchestrator, bridging
between the compiler that generates stage and policy instances, and
the pipeline that executes them sequentially under a scheduling
strategy.

Classes
--------
BaseKernel
    Core kernel responsible for pipeline construction, stage
    assembly, and sample execution.
"""

from typing import TYPE_CHECKING

from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.kernel.core.abstract_kernel import (
    AbstractKernel,
)
from saxs.saxs.core.kernel.core.back.kernel_compiler import BaseCompiler
from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.stage.abstract_stage import AbstractStage

if TYPE_CHECKING:
    from saxs.saxs.core.kernel.core.back.buffer import Buffer
    from saxs.saxs.core.pipeline.scheduler.scheduler import AbstractScheduler
    from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
        ChainingPolicy,
    )


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
    ):
        self.scheduler = scheduler
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
        )

    def _get_initial_stage(
        self,
        _execution_order: list[str],
    ) -> list[AbstractStage]:
        """Get init stages ordered.

        Retrieve the initial stages in order from the compiled stage
        buffer.

        Parameters
        ----------
        _execution_order : list of str
            Ordered list of stage identifiers defining the execution
            sequence.

        Returns
        -------
        list of AbstractStage
            A list of stage instances corresponding to the provided
            execution order.
        """
        _initial_stages: list[AbstractStage] = []

        for _stage_id in _execution_order:
            _stage = self.stage_buffer.get(_stage_id)
            if _stage:
                _initial_stages.append(_stage)

        return _initial_stages

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the kernel pipeline on the given sample.

        This method executes the pipeline using the configured
        scheduler until all stages have completed processing.

        Parameters
        ----------
        init_sample : SAXSSample
            The initial SAXS sample to process through the pipeline.

        Returns
        -------
        SAXSSample
            The final processed sample after pipeline completion.
        """
        return self.pipeline.run(init_sample)

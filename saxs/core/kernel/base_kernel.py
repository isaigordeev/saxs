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

from saxs.core.kernel.abstract_kernel import (
    IAbstractKernel,
)
from saxs.core.kernel.back.kernel_compiler import BaseCompiler
from saxs.core.pipeline.pipeline import Pipeline
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.types.sample import SAXSSample

if TYPE_CHECKING:
    from saxs.core.kernel.back.buffer import Buffer
    from saxs.core.pipeline.scheduler.scheduler import IAbstractScheduler
    from saxs.core.stage.policy.abstract_chaining_policy import (
        IAbstractChainingPolicy,
    )


class BaseKernel(IAbstractKernel):
    """
    Base kernel class.

    Encapsulates orchestration of:
    - pipeline building
    - scheduler wiring
    - sample creation.
    """

    def __init__(
        self,
        scheduler: "IAbstractScheduler",
    ):
        self.scheduler = scheduler
        self.execution_order: list[str] = []

        self.build()

    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""
        _stage_decl, _policy_decl, _execution_order = self.define()

        _comp = BaseCompiler()

        self.stage_buffer: Buffer[IAbstractStage]
        self.policy_buffer: Buffer[IAbstractChainingPolicy]

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
    ) -> list[IAbstractStage]:
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
        _initial_stages: list[IAbstractStage] = []

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

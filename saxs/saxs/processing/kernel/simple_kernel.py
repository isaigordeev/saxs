"""
simple_kernel.py.

This module defines the `SimpleKernel`, a concrete implementation of
`BaseKernel` that sets up a small SAXS (Small-Angle X-ray
Scattering) processing pipeline.

The kernel defines stages, policies, and execution order in a
hardcoded example pipeline, including:

- Cut, Filter, and Background stages
- Peak finding and processing stages
- Single-stage chaining policies with conditions

The kernel integrates these declarations with the scheduler and
pipeline infrastructure for execution.

Classes
-------
SimpleKernel(BaseKernel)
    Concrete kernel implementing a predefined SAXS processing
    pipeline.
"""

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec, StageSpec
from saxs.saxs.core.kernel.core.base_kernel import BaseKernel
from saxs.saxs.core.kernel.registry.kernel_registry import KernelRegistry
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.pipeline.condition.constant_true_condition import (
    TrueCondition,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.processing.stage.background.background import (
    BackgroundStage,
)
from saxs.saxs.processing.stage.cut.cut import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)


class SimpleKernel(BaseKernel):
    """
    Concrete kernel defining a simple SAXS processing pipeline.

    `SimpleKernel` implements a small, predefined pipeline by
    registering stages and policies using a `KernelRegistry`. The
    pipeline includes filtering and peak-processing stages and
    uses single-stage chaining policies to determine stage execution
    flow based on stage-specific conditions.

    Inherits
    --------
    BaseKernel
        Provides the base orchestration for building and executing
        pipelines.
    """

    def define(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
        """
        Define the pipeline stages, policies, and execution order.

        This method builds a predefined pipeline with stages and
        policies, registers them in a `KernelRegistry`, and returns
        the corresponding buffers and execution order for the
        kernel.

        Returns
        -------
        stage_specs : Buffer of StageSpec
            Buffer containing all stage declarations in the
            pipeline.
        policy_specs : Buffer of PolicySpec
            Buffer containing all policy declarations.
        execution_order : list of str
            Ordered list of stage IDs specifying the execution
            sequence.
        """
        _kernel_registry = KernelRegistry()

        # ---- Define policies ----
        peaks_policy = PolicySpec(
            id="peaks_policy",
            policy_cls=SingleStageChainingPolicy,
            condition=ChainingPeakCondition,
            condition_kwargs={"key": "peaks"},
            pending_stages=["process_fit_peak"],
        )
        fit_policy = PolicySpec(
            id="fit_policy",
            policy_cls=SingleStageChainingPolicy,
            condition=TrueCondition,
            condition_kwargs={},
            pending_stages=["find_peaks"],
        )

        _kernel_registry.register_policy(peaks_policy)
        _kernel_registry.register_policy(fit_policy)

        # ---- Define stages ----
        _kernel_registry.register_stage(
            StageSpec(
                id="cut",
                stage_cls=CutStage,
                kwargs={"cut_point": 200},
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id="filter",
                stage_cls=FilterStage,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id="background",
                stage_cls=BackgroundStage,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id="find_peaks",
                stage_cls=FindAllPeaksStage,
                policy_id="peaks_policy",
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id="process_fit_peak",
                stage_cls=ProcessFitPeakStage,
                policy_id="fit_policy",
            ),
        )

        return (
            _kernel_registry.stage_specs,
            _kernel_registry.policy_specs,
            _kernel_registry.execution_order,
        )

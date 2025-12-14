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
    DEFAULT_BACKG_META,
    BackgroundStage,
)
from saxs.saxs.processing.stage.cut.cut import DEFAULT_CUT_META, CutStage
from saxs.saxs.processing.stage.filter.filter import FilterStage
from saxs.saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.saxs.processing.stage.peak.process_peak import (
    ProcessPeakStage,
)
from saxs.saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    DEFAULT_PEAK_PROCESS_META,
)


class DefaultKernel(BaseKernel):
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
        find_peak_policy = PolicySpec(
            id_="find_peak_policy",
            policy_cls=SingleStageChainingPolicy,
            condition=ChainingPeakCondition,
            pending_stages=["process_peak"],
        )
        process_peak_policy = PolicySpec(
            id_="process_peak_policy",
            policy_cls=SingleStageChainingPolicy,
            condition=TrueCondition,
            pending_stages=["find_peaks"],
        )

        _kernel_registry.register_policy(find_peak_policy)
        _kernel_registry.register_policy(process_peak_policy)

        # ---- Define stages ----
        _kernel_registry.register_stage(
            StageSpec(
                id_="cut",
                stage_cls=CutStage,
                metadata=DEFAULT_CUT_META,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id_="filter",
                stage_cls=FilterStage,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id_="background",
                stage_cls=BackgroundStage,
                metadata=DEFAULT_BACKG_META,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id_="find_peaks",
                stage_cls=FindPeakStage,
                policy_id="find_peak_policy",
                metadata=DEFAULT_PEAK_FIND_META,
            ),
        )
        _kernel_registry.register_stage(
            StageSpec(
                id_="process_peak",
                stage_cls=ProcessPeakStage,
                policy_id="process_peak_policy",
                metadata=DEFAULT_PEAK_PROCESS_META,
            ),
        )

        return (
            _kernel_registry.stage_specs,
            _kernel_registry.policy_specs,
            _kernel_registry.execution_order,
        )

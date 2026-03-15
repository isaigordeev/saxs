"""Default SAXS processing kernel.

Defines a predefined pipeline: Cut -> Filter -> Background -> FindPeak -> ProcessPeak
"""

from saxs.core.condition import ChainingPeakCondition, TrueCondition
from saxs.core.kernel import BaseKernel
from saxs.core.specs import Buffer, KernelRegistry, PolicySpec, StageSpec
from saxs.core.stage import SingleStageChainingPolicy
from saxs.processing.stages.background import (
    DEFAULT_BACKG_META,
    BackgroundStage,
)
from saxs.processing.stages.cut import DEFAULT_CUT_META, CutStage
from saxs.processing.stages.filter import FilterStage
from saxs.processing.stages.peak import (
    DEFAULT_PEAK_FIND_META,
    DEFAULT_PEAK_PROCESS_META,
    FindPeakStage,
    ProcessPeakStage,
)


class DefaultKernel(BaseKernel):
    """Concrete kernel with a predefined SAXS processing pipeline."""

    def define(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
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
            StageSpec(id_="filter", stage_cls=FilterStage),
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
            initial=False,  # dynamically injected by find_peak_policy
        )

        return (
            _kernel_registry.stage_specs,
            _kernel_registry.policy_specs,
            _kernel_registry.execution_order,
        )

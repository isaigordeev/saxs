"""Default SAXS processing kernel.

Defines a predefined pipeline: Cut -> Filter -> Background -> FindPeak -> ProcessPeak
"""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import PolicySpec, StageSpec
from saxs.core.kernel.base_kernel import BaseKernel
from saxs.core.kernel.registry.kernel_registry import KernelRegistry
from saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.core.pipeline.condition.constant_true_condition import TrueCondition
from saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.processing.stage.background.background import (
    DEFAULT_BACKG_META,
    BackgroundStage,
)
from saxs.processing.stage.cut.cut import DEFAULT_CUT_META, CutStage
from saxs.processing.stage.filter.filter import FilterStage
from saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.processing.stage.peak.process_peak import ProcessPeakStage
from saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    DEFAULT_PEAK_PROCESS_META,
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

"""Stage and policy registry definitions."""

from saxs.core.kernel.base_registry import (
    ClassRegistry,
    PolicyRegistry,
    StageRegistry,
)
from saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.processing.stage.background.background import BackgroundStage
from saxs.processing.stage.cut.cut import CutStage
from saxs.processing.stage.filter.filter import FilterStage
from saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.processing.stage.peak.process_peak import ProcessPeakStage


def make_stage_registry() -> StageRegistry:
    return ClassRegistry()


def make_policy_registry() -> PolicyRegistry:
    return ClassRegistry()


stage_registry: StageRegistry = make_stage_registry()
stage_registry.register("CutStage", CutStage)
stage_registry.register("FilterStage", FilterStage)
stage_registry.register("BackgroundStage", BackgroundStage)
stage_registry.register("FindAllPeaksStage", FindPeakStage)
stage_registry.register("ProcessFitPeakStage", ProcessPeakStage)

policy_registry: PolicyRegistry = make_policy_registry()
policy_registry.register(
    "SingleStageChainingPolicy",
    SingleStageChainingPolicy,
)

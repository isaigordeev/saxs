"""Stage and policy registry definitions."""

from saxs.core.compiler import ClassRegistry
from saxs.core.stage import SingleStageChainingPolicy
from saxs.processing.stages.background import BackgroundStage
from saxs.processing.stages.cut import CutStage
from saxs.processing.stages.filter import FilterStage
from saxs.processing.stages.peak import FindPeakStage, ProcessPeakStage

stage_registry: ClassRegistry = ClassRegistry()
stage_registry.register("CutStage", CutStage)
stage_registry.register("FilterStage", FilterStage)
stage_registry.register("BackgroundStage", BackgroundStage)
stage_registry.register("FindAllPeaksStage", FindPeakStage)
stage_registry.register("ProcessFitPeakStage", ProcessPeakStage)

policy_registry: ClassRegistry = ClassRegistry()
policy_registry.register(
    "SingleStageChainingPolicy",
    SingleStageChainingPolicy,
)

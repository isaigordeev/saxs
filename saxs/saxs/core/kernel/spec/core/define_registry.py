# registry.py
from saxs.saxs.core.kernel.spec.core.registry import (
    StageRegistry,
    PolicyRegistry,
)
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)

stage_registry = StageRegistry()
stage_registry.register("CutStage", CutStage)
stage_registry.register("FilterStage", FilterStage)
stage_registry.register("FindAllPeaksStage", FindAllPeaksStage)
stage_registry.register("ProcessFitPeakStage", ProcessFitPeakStage)

policy_registry = PolicyRegistry()
policy_registry.register("SingleStageChainingPolicy", SingleStageChainingPolicy)

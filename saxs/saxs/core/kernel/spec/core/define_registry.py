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
from saxs.saxs.stage.policy.single_stage_policy import SingleStageChainingPolicy

stage_registry = StageRegistry()
stage_registry.register("cut", CutStage)
stage_registry.register("filter", FilterStage)
stage_registry.register("find_peaks", FindAllPeaksStage)
stage_registry.register("process_fit_peak", ProcessFitPeakStage)

policy_registry = PolicyRegistry()
policy_registry.register("single_stage_policy", SingleStageChainingPolicy)

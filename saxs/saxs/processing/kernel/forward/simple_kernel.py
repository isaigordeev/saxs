from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.kernel.forward.core.base_kernel import (
    BaseKernel,
)
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.processing.stage.filter.background_stage import BackgroundStage
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)


class SimpleKernel(BaseKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def define(self):
        # Example pipeline: Cut → Background → FindAllPeaks (with chaining)
        return [
            (CutStage, {"cut_point": 200}),
            (FilterStage),
            (BackgroundStage),
            (
                FindAllPeaksStage,
                {},
                SingleStageChainingPolicy(
                    ChainingPeakCondition("peaks"), ProcessFitPeakStage
                ),
            ),
        ]

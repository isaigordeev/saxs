from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.processing.kernels.abstract_kernel import (
    AbstractKernel,
    build_initial_stages,
)
from saxs.saxs.processing.stage.filter.background_stage import BackgroundStage
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)


class SimpleKernel(AbstractKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def pipeline_definition(self):
        # Example pipeline: Cut → Background → FindAllPeaks (with chaining)
        return [
            (CutStage, {"cut_point": 2}),
            BackgroundStage,
            (
                FindAllPeaksStage,
                {},
                SingleStageChainingPolicy(
                    ChainingPeakCondition("peaks"), ProcessFitPeakStage
                ),
            ),
        ]

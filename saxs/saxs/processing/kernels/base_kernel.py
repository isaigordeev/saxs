from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.compose_stage import CompositeRequstingStage
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.processing.kernels.abstract_kernel import AbstractKernel
from saxs.saxs.processing.stage.filter.background_stage import BackgroundStage
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)


class BaseKernel(AbstractKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def define_pipeline(self):
        _composite_callback = self.define_composite_peak_stage()

        return [
            (CutStage, {"cut_point": 200}),
            (FilterStage),
            (BackgroundStage),
            (
                FindAllPeaksStage,
                {},
                SingleStageChainingPolicy(
                    condition=ChainingPeakCondition("peaks"),
                    next_stage_cls=_composite_callback,
                ),
            ),
        ]

    def define_composite_peak_stage(self) -> AbstractStage:
        _params = {
            "main_stage_cls": ProcessFitPeakStage,
            "main_kwargs": {},
            "before": [],
            "after": [],
            "policy": None,
            "metadata": {},
        }
        return CompositeRequstingStage(**_params)

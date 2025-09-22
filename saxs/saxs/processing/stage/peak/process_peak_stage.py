#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractConditionalStage,
    AbstractSelfRepeatingConditionalStage,
)
from saxs.saxs.processing.functions import parabole


class AProcessPeakStage(AbstractConditionalStage):
    def __init__(self, chaining_stage, condition: SampleCondition):
        super().__init__(chaining_stage, condition)

    def _process(self, stage_data):
        return stage_data, None


class ProcessFitPeakStage(AProcessPeakStage):
    def _process(self, stage_data: SAXSSample):
        current_peak_index = stage_data.metadata.unwrap().get(
            "current_peak_index"
        )

        def current_peak_parabole(x, sigma, ampl):
            return parabole(
                x, self.current_q_state[current_peak_index], sigma, ampl
            )

        return stage_data, None

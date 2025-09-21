#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractConditionalStage,
    AbstractSelfRepeatingConditionalStage,
)


class AProcessPeakStage(AbstractConditionalStage):
    def __init__(self, chaining_stage, condition: SampleCondition):
        super().__init__(chaining_stage, condition)

    def _process(self, stage_data):
        return stage_data, None


class ProcessFitPeakStage(AProcessPeakStage):
    def __init__(self, chaining_stage, condition: SampleCondition):
        super().__init__(chaining_stage, condition)

    def _process(self, stage_data):
        return stage_data, None

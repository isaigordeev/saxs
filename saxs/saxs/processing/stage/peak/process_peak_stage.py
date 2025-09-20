#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractSelfRepeatingConditionalStage,
)


class ProcessPeakStage(AbstractSelfRepeatingConditionalStage):
    def __init__(self, condition: SampleCondition):
        super().__init__(condition)

    def _process(self, stage_data):
        return stage_data

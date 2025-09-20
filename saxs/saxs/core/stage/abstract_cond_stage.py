#
# Created by Isai GORDEEV on 20/09/2025.
#


from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage


class AbstractConditionalStage(AbstractStage):
    def __init__(
        self, chaining_stage: AbstractStage, condition: SampleCondition
    ):
        self.chaining_stage = chaining_stage
        self.condition = condition

    def get_next_stage(self):
        if self.condition.evaluate(self.metadata):
            state_to_inject = self.chaining_stage(self.condition)
            return [StageRequest(state_to_inject, self.metadata)]
        return []


class AbstractSelfRepeatingConditionalStage(AbstractStage):
    def __init__(self, condition: SampleCondition):
        self.condition = condition

    def get_next_stage(self):
        # if condition is true, reinsert itself into the pipeline
        if self.condition.evaluate(self.metadata):
            return [StageRequest(self, self.metadata)]
        return []

#
# Created by Isai GORDEEV on 20/09/2025.
#


from abc import abstractmethod

from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.request.abst_request import StageRequest


class AbstractConditionalStage(AbstractStage):
    def __init__(
        self, chaining_stage: AbstractStage, condition: SampleCondition
    ):
        self.chaining_stage = chaining_stage
        self.condition = condition

    def request_stage(self):
        if not self.condition:
            return []
        if self.condition.evaluate(self.metadata):
            state_to_inject = self.chaining_stage(
                self.chaining_stage, self.condition
            )
            return [StageApprovalRequest(state_to_inject, self.metadata)]
        return []


class AbstractRequestingStage(AbstractStage):
    def __init__(self, policy: ChainingPolicy):
        self.policy = policy

    def request_stage(self):
        if not self.policy:
            return []
        _request = self.create_request()
        return self.policy.request(_request)

    @abstractmethod
    def create_request(self) -> StageRequest:
        pass

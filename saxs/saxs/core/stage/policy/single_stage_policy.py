from typing import List, Type

from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.request.abst_request import StageRequest


class SingleStageChainingPolicy(ChainingPolicy):
    def __init__(
        self, condition: "StageCondition", next_stage_cls: Type[AbstractStage]
    ):
        self.condition = condition
        self.next_stage_cls = next_stage_cls

    def request(
        self, stage_metadata: StageRequest
    ) -> List["StageApprovalRequest"]:
        if not self.condition:
            return []
        _eval_metadata = stage_metadata.eval_metadata
        if self.condition.evaluate(_eval_metadata):
            _pass_metadata = stage_metadata.pass_metadata
            _scheduler_metadata = stage_metadata.scheduler_metadata
            return [
                StageApprovalRequest(
                    self.next_stage_cls(_pass_metadata), _scheduler_metadata
                )
            ]
        return []

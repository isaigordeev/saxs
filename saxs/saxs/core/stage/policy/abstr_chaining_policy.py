from abc import ABC, abstractmethod

from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.request.abst_request import StageRequest


class ChainingPolicy(ABC):
    def __init__(
        self,
        condition: "StageCondition",
        next_stage_cls: list[AbstractStage],
    ):
        self.condition = condition
        self.next_stage_cls: list[AbstractStage] = next_stage_cls

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest,
    ) -> list["StageApprovalRequest"]:
        """Stage request method.

        Decide which stages to chain based on stage metadata.
        """

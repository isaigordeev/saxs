from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypedDict

from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.stage.request.abst_request import StageRequest

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.condition.abstract_condition import (
        StageCondition,
    )
    from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class EvalSchemaDict(TypedDict, total=False):
    """Abstract eval dictionary schema."""


class ChainingPolicy(ABC):
    def __init__(
        self,
        condition: "StageCondition",
        pending_stages: list[IAbstractStage[Any]],
    ):
        self.condition = condition
        self.pending_stages: list[IAbstractStage[Any]] = pending_stages

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest,
    ) -> list["StageApprovalRequest"]:
        """Stage request method.

        Decide which stages to chain based on stage metadata.
        """

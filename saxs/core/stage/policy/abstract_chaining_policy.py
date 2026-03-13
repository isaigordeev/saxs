"""Abstract base class for stage chaining policies."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.request.abst_request import StageRequest

if TYPE_CHECKING:
    from saxs.core.pipeline.condition.abstract_condition import (
        StageCondition,
    )
    from saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class IAbstractChainingPolicy(ABC):
    """Determines which stages to inject after a stage completes.

    Attributes
    ----------
    condition : StageCondition
        Condition to evaluate for stage injection.
    pending_stages : list[IAbstractStage]
        Stages that may be injected.
    """

    def __init__(
        self,
        condition: "StageCondition",
        pending_stages: list[IAbstractStage],
    ):
        self.condition = condition
        self.pending_stages: list[IAbstractStage] = pending_stages

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest,
    ) -> list["StageApprovalRequest"]:
        """Evaluate condition and return approval requests."""

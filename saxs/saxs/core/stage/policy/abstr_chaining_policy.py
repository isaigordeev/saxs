from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypedDict

from saxs.saxs.core.stage.abstract_stage import IAbstractStage, TStageMetadata
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.condition.abstract_condition import (
        StageCondition,
    )
    from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class EvalSchemaDict(TypedDict, total=False):
    """Abstract eval dictionary schema."""


class ChainingPolicy(ABC, Generic[TStageMetadata]):
    def __init__(
        self,
        condition: "StageCondition",
        pending_stages: list[IAbstractStage[TStageMetadata]],
    ):
        self.condition = condition
        self.pending_stages: list[IAbstractStage[TStageMetadata]] = (
            pending_stages
        )

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest[EvalSchemaDict],
    ) -> list["StageApprovalRequest"]:
        """Stage request method.

        Decide which stages to chain based on stage metadata.
        """

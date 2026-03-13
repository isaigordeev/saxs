"""Abstract requesting stage that can chain to other stages."""

from abc import abstractmethod
from typing import Any

from saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)
from saxs.core.stage.request.abst_request import (
    IAbstractStageRequest,
)
from saxs.core.types.flow_metadata import FlowMetadata


class IAbstractRequestingStage(IAbstractStage):
    """Stage that can request injection of other stages via a policy."""

    def __init__(
        self,
        metadata: Any = None,
        policy: IAbstractChainingPolicy | None = None,
    ):
        self.policy = policy
        super().__init__(metadata)

    def request_stage(
        self,
        metadata: FlowMetadata,
    ) -> list[StageApprovalRequest]:
        """Generate stage approval requests via the chaining policy."""
        if self.policy is None:
            default = self.default_policy()
            self.policy = default

        if not self.policy:
            return []

        _request = self.create_request(metadata)

        if not _request:
            return []

        return self.policy.request(_request)

    def default_policy(self) -> IAbstractChainingPolicy | None:
        """Provide a fallback policy. Override in subclasses."""
        return None

    @abstractmethod
    def create_request(
        self,
        metadata: FlowMetadata,
    ) -> IAbstractStageRequest:
        """Create a stage request based on current flow metadata."""

from abc import ABC, abstractmethod
from typing import List

from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest


class ChainingPolicy(ABC):
    @abstractmethod
    def request(
        self, request_metadata: StageRequest
    ) -> List["StageApprovalRequest"]:
        """Decide which stages to chain based on stage metadata."""
        pass

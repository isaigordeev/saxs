"""Insertion policies for the scheduler."""

from abc import ABC, abstractmethod

from saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)


class InsertionPolicy(ABC):
    """Decides whether a requested stage should be added to the queue."""

    @abstractmethod
    def __call__(self, request: StageApprovalRequest) -> bool:
        """Return True if the stage should be inserted."""


class AlwaysInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageApprovalRequest) -> bool:
        return True


class NeverInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageApprovalRequest) -> bool:
        return False


class SaturationInsertPolicy(InsertionPolicy):
    """Accept up to N stage insertions."""

    def __init__(self, saturation: int = 6):
        self._saturation = saturation
        self._calls = 0

    def __call__(self, request: StageApprovalRequest) -> bool:
        if self._calls < self._saturation:
            self._calls += 1
            return True
        return False

# Created by Isai Gordeev on 20/09/2025.

from abc import ABC, abstractmethod

from saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)


class InsertionPolicy(ABC):
    """Abstract insertion policy.

    Base class for insertion policies.
    Policies decide whether a StageRequest should be
    inserted into the scheduler's queue.
    """

    @abstractmethod
    def __call__(self, request: StageApprovalRequest) -> bool:
        """Calculate predicat in order to approve stage insertion.

        Return True if the stage should be inserted,
        False otherwise.
        """


class AlwaysInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageApprovalRequest) -> bool:
        return True


class NeverInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageApprovalRequest) -> bool:
        return False


class SaturationInsertPolicy(InsertionPolicy):
    _calls = 0
    _saturation = 6

    def __init__(self, saturation: int = 6):
        self._saturation = saturation

    def __call__(self, request: StageApprovalRequest) -> bool:
        if self._calls < self._saturation:
            self._calls += 1
            return True
        return False


class MetadataKeyPolicy(InsertionPolicy):
    """Only insert stage if metadata contains a specific key."""

    def __init__(self, key: str):
        self.key = key

    def __call__(self, request: StageApprovalRequest) -> bool:
        return self.key in request.approval_metadata.unwrap()

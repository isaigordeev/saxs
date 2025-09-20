#
# Created by Isai GORDEEV on 20/09/2025.
#

from abc import ABC, abstractmethod

from saxs.saxs.core.pipeline.scheduler.stage_request import StageRequest


class InsertionPolicy(ABC):
    """
    Base class for insertion policies.
    Policies decide whether a StageRequest should be inserted into the ]
    scheduler's queue.
    """

    @abstractmethod
    def __call__(self, request: StageRequest) -> bool:
        """Return True if the stage should be inserted, False otherwise."""
        pass


class AlwaysInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageRequest) -> bool:
        return True


class NeverInsertPolicy(InsertionPolicy):
    def __call__(self, request: StageRequest) -> bool:
        return False


class MetadataKeyPolicy(InsertionPolicy):
    """
    Only insert stage if metadata contains a specific key.
    """

    def __init__(self, key: str):
        self.key = key

    def __call__(self, request: StageRequest) -> bool:
        return self.key in request.metadata.data

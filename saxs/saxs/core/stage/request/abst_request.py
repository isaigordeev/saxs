from abc import ABC, abstractmethod
from dataclasses import dataclass

from saxs.saxs.core.types.scheduler_objects import AbstractSchedulerMetadata
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


@dataclass(frozen=True)
class AbstractStageRequest:
    """
    Base class for stage addition requests.
    The position (next/end) is determined by the Scheduler/Pipeline.
    """

    pass


@dataclass(frozen=True)
class StageRequest(AbstractStageRequest):
    eval_metadata: AbstractStageMetadata
    pass_metadata: AbstractStageMetadata
    scheduler_metadata: AbstractSchedulerMetadata

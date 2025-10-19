#
# Created by Isai GORDEEV on 20/09/2025.
#


from dataclasses import dataclass

from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.types.scheduler_objects import AbstractSchedulerMetadata


@dataclass(frozen=True)
class AbstractStageApprovalRequest:
    """
    Base class for stage addition requests.
    The position (next/end) is determined by the Scheduler/Pipeline.
    """

    pass


@dataclass(frozen=True)
class StageApprovalRequest(AbstractStageApprovalRequest):
    stage: AbstractStage
    metadata: AbstractSchedulerMetadata

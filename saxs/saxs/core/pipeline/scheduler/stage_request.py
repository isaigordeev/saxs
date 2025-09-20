#
# Created by Isai GORDEEV on 20/09/2025.
#


from dataclasses import dataclass
from typing import Callable

from saxs.saxs.data.stage_objects import AbstractStageMetadata
from saxs.saxs.pipeline.stage.abstract_stage import AbstractStage


@dataclass(frozen=True)
class AbstractStageRequest:
    """
    Base class for stage addition requests.
    The position (next/end) is determined by the Scheduler/Pipeline.
    """

    pass


@dataclass(frozen=True)
class StageRequest(AbstractStageRequest):
    stage: AbstractStage
    metadata: AbstractStageMetadata

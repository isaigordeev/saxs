# # Created by Isai GORDEEV on 20/09/2025.  #


from dataclasses import dataclass
from typing import Any

from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


@dataclass(frozen=True)
class AbstractStageApprovalRequest:
    """Base class for stage addition requests.

    The position (next/end) is determined by the Scheduler/Pipeline.
    """


@dataclass(frozen=True)
class StageApprovalRequest(AbstractStageApprovalRequest):
    """Concrete implementation of a stage approval request.

    This class represents a request to add a new stage to the
    pipeline with its metadata. The request is immutable to ensure
    data integrity during approval. The scheduler/pipeline
    determines the insertion position.

    Parameters
    ----------
    stage : AbstractStage
        The stage to be added to the pipeline. This represents the
        actual processing unit that will be executed.
    metadata : AbstractStageMetadata
        Associated metadata for the stage. Contains configuration
        and other information needed for stage execution and
        scheduling.  Must implement the AbstractStageMetadata
        interface.
    """

    stage: AbstractStage
    metadata: AbstractStageMetadata[dict[str, Any]]

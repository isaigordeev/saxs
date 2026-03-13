"""Stage approval request types."""

from dataclasses import dataclass

from saxs.core.stage.abstract_stage import IAbstractStage


@dataclass(frozen=True)
class StageApprovalRequest:
    """Request for a stage to be approved and added to the pipeline.

    Attributes
    ----------
    stage : IAbstractStage
        The stage to be added.
    """

    stage: IAbstractStage

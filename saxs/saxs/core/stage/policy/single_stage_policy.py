"""
single_stage_policy.py.

Implements a single-stage chaining policy for SAXS pipelines.

This policy allows a stage to request the injection of at most one
next stage based on a condition. If the condition passes, the
requested stage is instantiated and wrapped in a
StageApprovalRequest with associated scheduler metadata.
"""

from typing import Any

from saxs.logging.logger import get_logger
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)

logger = get_logger(__name__, "policy")
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    ApprovalMetadata,
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
    AbstractChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import (
    StageRequest,
)

#  probably there we need to unwire
#  TStageMetadata from TStageMetadata


class SingleStageChainingPolicy(AbstractChainingPolicy):
    """
    Single-stage chaining policy.

    Allows a stage to request at most one next stage based on a
    condition. Evaluates the condition against the stage's
    evaluation metadata. If it passes, the next stage is
    instantiated and returned as a StageApprovalRequest.

    Attributes
    ----------
    condition : StageCondition
        Condition used to evaluate whether to inject the next stage.
    next_stage_cls : list of AbstractStage
        List containing the next stage class. Must contain at most
        one element.
    """

    def __new__(
        cls,
        condition: StageCondition,  # noqa: ARG004
        pending_stages: list[IAbstractStage[Any]],
    ):
        """
        Allocate a new instance and validate input.

        Parameters
        ----------
        condition : StageCondition Condition used to determine
        stage injection.  next_stage_cls : list of AbstractStage
            List containing the next stage class. Must contain at
            most one element.

        Raises
        ------
        ValueError
            If more than one next stage is provided.
        """
        # Validate before object allocation
        if len(pending_stages) > 1:
            msg = (
                f"{cls.__name__} expects at most one next stage, "
                f"got {len(pending_stages)}"
            )
            raise ValueError(msg)

        return super().__new__(cls)

    def request(
        self,
        request_metadata: StageRequest,
    ) -> list[StageApprovalRequest]:
        """
        Evaluate the condition and return a stage request.

        Parameters
        ----------
        stage_metadata : StageRequest
            Metadata from the current stage, including evaluation,
            pass, and scheduler info.

        Returns
        -------
        list of StageApprovalRequest
            A list containing a single StageApprovalRequest if the
            condition passes, otherwise an empty list.
        """
        if not self.condition:
            logger.info("No condition set, skipping injection")
            return []

        _eval_metadata = request_metadata.condition_eval_metadata

        if self.condition.evaluate(eval_metadata=_eval_metadata):
            _flow_metadata = request_metadata.flow_metadata
            _approval_metadata = ApprovalMetadata(value={})

            _pending_stage: IAbstractStage[Any] = self.pending_stages[
                0
            ]  # there is only one stage

            logger.stage_info(
                _pending_stage.__class__.__name__,
                "Injecting stage",
                condition=self.condition.__class__.__name__,
                approval_metadata=_approval_metadata,
                flow_metadata=_flow_metadata,
            )

            return [
                StageApprovalRequest(
                    stage=_pending_stage,
                    approval_metadata=_approval_metadata,
                ),
            ]

        logger.info("Condition failed | No stage injected")
        return []

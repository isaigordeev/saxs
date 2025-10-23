"""
single_stage_policy.py.

Implements a single-stage chaining policy for SAXS pipelines.

This policy allows a stage to request the injection of at most one
next stage based on a condition. If the condition passes, the
requested stage is instantiated and wrapped in a StageApprovalRequest
with associated scheduler metadata.
"""

from typing import TYPE_CHECKING

from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.request.abst_request import StageRequest

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.condition.abstract_condition import (
        StageCondition,
    )


class SingleStageChainingPolicy(ChainingPolicy):
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
        condition: "StageCondition",  # noqa: ARG004
        pending_stages: list[AbstractStage],
    ):
        """
        Allocate a new instance and validate input.

        Parameters
        ----------
        condition : StageCondition
            Condition used to determine stage injection.
        next_stage_cls : list of AbstractStage
            List containing the next stage class. Must contain at most
            one element.

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
        stage_metadata: StageRequest,
    ) -> list["StageApprovalRequest"]:
        """
        Evaluate the condition and return a stage request if allowed.

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
            logger.info(
                f"\n{'=' * 30}\n[{self.__class__.__name__}]",
                f"No condition set, skipping injection.\n{'=' * 30}",
            )
            return []

        _eval_metadata = stage_metadata.condition_eval_metadata

        logger.info(
            f"\n{'=' * 30}\n[{self.__class__.__name__}] Evaluating condition '{self.condition.__class__.__name__}' "
            f"for stage '{_eval_metadata}' with metadata: {_eval_metadata.values}\n{'=' * 30}"
        )

        if self.condition.evaluate(eval_metadata=_eval_metadata):
            _pass_metadata = stage_metadata.sample_metadata
            _scheduler_metadata = stage_metadata.scheduler_metadata

            _pending_stage: AbstractStage = self.pending_stages[-1]

            logger.info(
                f"\n{'=' * 30}\n[{self.__class__.__name__}] "
                "Condition passed -> Injecting stage "
                f"'{_pending_stage.__class__.__name__}' with metadata:"
                " {_pass_metadata.values}\n{'=' * 30}",
            )

            return [
                StageApprovalRequest(
                    stage=_pending_stage,
                    metadata=_pass_metadata,
                ),
            ]

        logger.info(
            f"\n{'=' * 30}\n[{self.__class__.__name__}] Condition failed → No stage injected for '{self.pending_stages}'\n{'=' * 30}"
        )
        return []

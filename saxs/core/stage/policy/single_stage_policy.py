"""Single-stage chaining policy."""

from saxs.logging.logger import get_logger

from saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)
from saxs.core.stage.request.abst_request import StageRequest

logger = get_logger(__name__, "policy")


class SingleStageChainingPolicy(IAbstractChainingPolicy):
    """Policy that injects at most one next stage based on a condition."""

    def __init__(
        self,
        condition: StageCondition,
        pending_stages: list[IAbstractStage],
    ):
        if len(pending_stages) > 1:
            msg = (
                f"{self.__class__.__name__} expects at most one next stage, "
                f"got {len(pending_stages)}"
            )
            raise ValueError(msg)
        super().__init__(condition, pending_stages)

    def request(
        self,
        request_metadata: StageRequest,
    ) -> list[StageApprovalRequest]:
        """Evaluate condition and return a stage request if it passes."""
        if not self.condition:
            logger.info("No condition set, skipping injection")
            return []

        _eval_metadata = request_metadata.condition_eval_metadata

        if self.condition.evaluate(eval_metadata=_eval_metadata):
            _pending_stage: IAbstractStage = self.pending_stages[0]

            logger.stage_info(
                _pending_stage.__class__.__name__,
                "Injecting stage",
                condition=self.condition.__class__.__name__,
            )

            return [
                StageApprovalRequest(stage=_pending_stage),
            ]

        logger.info("Condition failed | No stage injected")
        return []

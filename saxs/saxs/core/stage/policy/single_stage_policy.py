from typing import List, Type

from saxs.logging.logger import logger
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.request.abst_request import StageRequest


class SingleStageChainingPolicy(ChainingPolicy):
    def __new__(cls, condition: "StageCondition", next_stage_cls: list):
        # Validate before object allocation
        assert len(next_stage_cls) <= 1, (
            f"{cls.__name__} expects exactly no more than one next stage, "
            f"got {len(next_stage_cls)}"
        )
        return super().__new__(cls)

    def request(
        self, stage_metadata: StageRequest
    ) -> List["StageApprovalRequest"]:
        if not self.condition:
            logger.info(
                f"\n{'=' * 30}\n[{self.__class__.__name__}] No condition set, skipping injection.\n{'=' * 30}"
            )
            return []

        _eval_metadata = stage_metadata.eval_metadata

        logger.info(
            f"\n{'=' * 30}\n[{self.__class__.__name__}] Evaluating condition '{self.condition.__class__.__name__}' "
            f"for stage '{_eval_metadata}' with metadata: {_eval_metadata.values}\n{'=' * 30}"
        )

        if self.condition.evaluate(_eval_metadata):
            _pass_metadata = stage_metadata.pass_metadata
            _scheduler_metadata = stage_metadata.scheduler_metadata

            logger.info(
                f"\n{'=' * 30}\n[{self.__class__.__name__}] Condition passed → Injecting stage "
                f"'{self.next_stage_cls.__name__}' with metadata: {_pass_metadata.values}\n{'=' * 30}"
            )

            single_requested_stage_cls = self.next_stage_cls[0]

            return [
                StageApprovalRequest(
                    single_requested_stage_cls(
                        metadata=_pass_metadata,
                    ),
                    _scheduler_metadata,
                )
            ]

        logger.info(
            f"\n{'=' * 30}\n[{self.__class__.__name__}] Condition failed → No stage injected for '{self.next_stage_cls}'\n{'=' * 30}"
        )
        return []

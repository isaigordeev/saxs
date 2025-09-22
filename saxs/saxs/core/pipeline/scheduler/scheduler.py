#
# Created by Isai GORDEEV on 20/09/2025.
#
from abc import ABC, abstractmethod
from collections import deque
from typing import List, Optional

from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    AlwaysInsertPolicy,
    InsertionPolicy,
)
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)


class AbstractScheduler(ABC):
    """Abstract base class for all schedulers."""

    def __init__(
        self,
        init_stages: Optional[List] = None,
        insertion_policy: Optional[InsertionPolicy] = None,
    ):
        logger.info(
            f"\n{'=' * 30}\n[Scheduler] Init_stages: {init_stages}'\n{'=' * 30}"
        )
        self._queue = deque(init_stages or [])
        self._insertion_policy = insertion_policy or AlwaysInsertPolicy()

    @abstractmethod
    def run(self, init_sample):
        pass


class BaseScheduler(AbstractScheduler):
    """Executes stages sequentially and appends new requests to the end of the queue."""

    def run(self, init_sample):
        queue = self._queue
        sample = init_sample
        step = 1

        logger.info(f"\n{'=' * 30}\n[Scheduler] Queue: {queue}'\n{'=' * 30}")

        while queue:
            stage = queue.popleft()
            stage_name = stage.__class__.__name__

            logger.info(
                f"\n{'=' * 30}\n[Scheduler] Step {step}: Running stage {stage}'{stage_name}'"
                f" on sample '{sample}'\n{'=' * 30}"
            )

            # Process stage
            sample = stage.process(sample)

            logger.info(
                f"\n[Scheduler] Stage '{stage_name}' completed. Sample metadata: {sample.get_metadata_dict()}\n"
            )

            # Collect new stage requests
            requests: List[StageApprovalRequest] = stage.request_stage()

            if requests:
                logger.info(
                    f"\n[Scheduler] Stage '{stage_name}' generated {len(requests)} request(s)."
                )
            else:
                logger.info(
                    f"\n[Scheduler] Stage '{stage_name}' generated no requests.\n"
                )

            for req in requests:
                req_stage_name = req.stage.__class__.__name__
                if self._insertion_policy(req):  # policy decides
                    queue.append(req.stage)
                    logger.info(
                        f"\n[Scheduler] Request {req} approved → Stage '{req_stage_name}' appended to queue."
                    )
                else:
                    logger.info(
                        f"\n[Scheduler] Request {req} rejected → Stage '{req_stage_name}' not appended."
                    )

            step += 1

        logger.info(
            f"\n{'=' * 30}\n[Scheduler] Pipeline completed. Final sample metadata: {sample.get_metadata_dict()}\n{'=' * 30}"
        )
        return sample

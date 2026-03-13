"""Pipeline scheduler.

Orchestrates sequential execution of SAXS processing stages.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import TYPE_CHECKING, Any

from saxs.logging.logger import get_scheduler_logger

logger = get_scheduler_logger(__name__)

from saxs.core.pipeline.scheduler.policy.insertion_policy import (
    AlwaysInsertPolicy,
    InsertionPolicy,
)
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample
from saxs.core.types.scheduler_metadata import SchedulerMetadata

if TYPE_CHECKING:
    from saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class IAbstractScheduler(ABC):
    """Abstract base class for schedulers."""

    _metadata: SchedulerMetadata

    def __init__(
        self,
        init_stages: list[IAbstractStage] | None = None,
        insertion_policy: InsertionPolicy | None = None,
    ):
        logger.scheduler_info(
            "Initializing scheduler",
            stages_count=len(init_stages) if init_stages else 0,
            policy=insertion_policy.__class__.__name__
            if insertion_policy
            else "AlwaysInsertPolicy",
        )
        self._queue: deque[IAbstractStage] = deque(init_stages or [])
        self._insertion_policy = insertion_policy or AlwaysInsertPolicy()

    @abstractmethod
    def run(
        self,
        init_sample: SAXSSample,
        init_flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Run the scheduler pipeline."""

    def enqueue_initial_stages(
        self,
        initial_stages: list[IAbstractStage],
    ) -> None:
        """Add initial stages to the processing queue."""
        self._queue.extend(initial_stages)


class BaseScheduler(IAbstractScheduler):
    """Executes stages sequentially in FIFO order."""

    def run(
        self,
        init_sample: SAXSSample,
        init_flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Execute all stages sequentially."""
        queue = self._queue
        _sample = init_sample
        _flow_metadata = init_flow_metadata
        step = 1

        logger.scheduler_info(
            "Pipeline started",
            queue_size=len(queue),
        )

        while queue:
            stage: IAbstractStage = queue.popleft()
            stage_name = stage.__class__.__name__

            logger.scheduler_info(
                f"Step {step}: Running {stage_name}",
                queue_size=len(queue),
            )

            _sample, _flow_metadata = stage.process(
                sample=_sample,
                flow_metadata=_flow_metadata,
            )

            logger.scheduler_info(f"{stage_name} completed")

            requests: list[StageApprovalRequest] = stage.request_stage(
                _flow_metadata,
            )

            if requests:
                logger.scheduler_info(
                    f"{stage_name} requested {len(requests)} stage(s)",
                )

            for req in requests:
                req_stage_name = req.stage.__class__.__name__
                if self._insertion_policy(req):
                    queue.append(req.stage)
                    logger.scheduler_info(
                        f"Approved: {req_stage_name}",
                        queue_size=len(queue),
                    )
                else:
                    logger.scheduler_info(
                        f"Rejected: {req_stage_name}",
                        queue_size=len(queue),
                    )

            step += 1

        logger.scheduler_info(
            "Pipeline completed",
            total_steps=step - 1,
        )
        return _sample

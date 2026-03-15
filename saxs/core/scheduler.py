"""Pipeline scheduler and insertion policies.

Orchestrates sequential execution of SAXS processing stages.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import TYPE_CHECKING

from saxs.logging.logger import get_scheduler_logger

from saxs.core.stage import IAbstractStage
from saxs.core.types import FlowMetadata, SAXSSample, SchedulerMetadata

if TYPE_CHECKING:
    from saxs.core.stage import StageApprovalRequest

logger = get_scheduler_logger(__name__)


# ---------------------------------------------------------------------------
# Insertion policies
# ---------------------------------------------------------------------------


class InsertionPolicy(ABC):
    """Decides whether a requested stage should be added to the queue."""

    @abstractmethod
    def __call__(self, request: "StageApprovalRequest") -> bool:
        """Return True if the stage should be inserted."""


class AlwaysInsertPolicy(InsertionPolicy):
    def __call__(self, request: "StageApprovalRequest") -> bool:
        return True


class NeverInsertPolicy(InsertionPolicy):
    def __call__(self, request: "StageApprovalRequest") -> bool:
        return False


class SaturationInsertPolicy(InsertionPolicy):
    """Accept up to N stage insertions."""

    def __init__(self, saturation: int = 6):
        self._saturation = saturation
        self._calls = 0

    def __call__(self, request: "StageApprovalRequest") -> bool:
        if self._calls < self._saturation:
            self._calls += 1
            return True
        return False


# ---------------------------------------------------------------------------
# Schedulers
# ---------------------------------------------------------------------------


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


__all__ = [
    "AlwaysInsertPolicy",
    "BaseScheduler",
    "IAbstractScheduler",
    "InsertionPolicy",
    "NeverInsertPolicy",
    "SaturationInsertPolicy",
]

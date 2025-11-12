"""
scheduler.py.

This module defines abstract and base scheduler classes responsible
for orchestrating the sequential execution of SAXS (Small-Angle
X-ray Scattering) processing stages within a pipeline. Each
scheduler manages a queue of `AbstractStage` objects that process
`SAXSSample` instances, applying an insertion policy to dynamically
adjust the execution order based on stage-generated requests.

Classes
--------
AbstractScheduler
    Base class defining the scheduler interface.
BaseScheduler
    Concrete scheduler that executes stages sequentially and manages
    new stage requests according to an insertion policy.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import TYPE_CHECKING, Any

from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    AlwaysInsertPolicy,
    InsertionPolicy,
)
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.flow_metadata import FlowMetadata
from saxs.saxs.core.types.metadata import TMetadataKeys, TMetadataSchemaDict
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.scheduler_metadata import (
    ESchedulerMetadataDictKeys,
    SchedulerMetadata,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class AbstractScheduler(ABC):
    """Abstract base class for all schedulers.

    A scheduler manages the execution of a queue of processing
    stages (`AbstractStage`) applied to a `SAXSSample`. It defines
    the general structure for running the pipeline and provides a
    consistent interface for concrete scheduler implementations.

    Attributes
    ----------
    _metadata : AbstractSchedulerMetadata
        Stores scheduler-level metadata.
    _queue : collections.deque
        Queue holding pending stages to execute.
    _insertion_policy : InsertionPolicy
        Policy controlling how new stages are added to the queue.
    """

    _metadata: SchedulerMetadata

    def __init__(
        self,
        init_stages: list[IAbstractStage[Any]] | None = None,
        insertion_policy: InsertionPolicy | None = None,
    ):
        logger.info(
            f"\n{'=' * 30}\n[Scheduler] Init_stages:\n"
            f" {init_stages}'\n{'=' * 30}\n",
        )
        self._queue = deque(init_stages or [])
        self._insertion_policy = insertion_policy or AlwaysInsertPolicy()

    @abstractmethod
    def run(
        self,
        init_sample: SAXSSample,
        init_flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Run the scheduler pipeline.

        Parameters
        ----------
        init_sample : SAXSSample
            The initial sample to process.

        Returns
        -------
        SAXSSample
            The processed sample after all stages complete.
        """

    def enqueue_initial_stages(
        self,
        initial_stages: list[IAbstractStage[Any]],
    ) -> None:
        """Add initial stages to the processing queue.

        Parameters
        ----------
        initial_stages : list of AbstractStage
            List of stage instances to enqueue.
        """
        self._queue.extend(initial_stages)


class BaseScheduler(AbstractScheduler):
    """Concrete scheduler that executes stages sequentially.

    The `BaseScheduler` processes each stage in the queue in FIFO
    order. After a stage runs, it collects and evaluates
    stage-generated requests using the configured insertion policy,
    appending approved stages to the queue.

    This implementation provides a simple linear workflow, suitable
    for most SAXS data processing pipelines.
    """

    def run(
        self,
        init_sample: SAXSSample,
        init_flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Execute all stages in the scheduler sequentially.

        Each stage processes the sample and may generate one or more
        stage-approval requests for additional processing steps.

        Parameters
        ----------
        init_sample : SAXSSample
            The initial sample to process.

        Returns
        -------
        SAXSSample
            The final processed sample after all stages complete.
        """
        queue = self._queue

        _sample = init_sample
        _flow_metadata = init_flow_metadata
        step = 1

        logger.info(f"\n{'=' * 30}\n[Scheduler] Queue: {queue}'\n{'=' * 30}\n")

        while queue:
            stage: IAbstractStage[Any] = queue.popleft()
            stage_name = stage.__class__.__name__

            logger.info(
                f"\n{'=' * 30}\n[Scheduler] Step {step}:"
                f" Running stage {stage.__class__}"
                f" on sample '{_sample.__class__}'\n{'=' * 30}\n",
            )

            # Process stage
            _sample, _flow_metadata = stage.process(
                sample=_sample,
                flow_metadata=_flow_metadata,
            )

            logger.info(
                f"\n[Scheduler] Stage '{stage_name}' completed."
                f"Sample metadata: {_sample.__class__}\n",
            )

            # Collect new stage requests
            requests: list[StageApprovalRequest] = stage.request_stage(
                _flow_metadata,
            )  # now it is specific to a stage not to a scheduler

            if requests:
                logger.info(
                    f"\n[Scheduler] Stage '{stage_name}' generated"
                    f" {len(requests)} request(s).\n",
                )
            else:
                logger.info(
                    f"\n[Scheduler] Stage '{stage_name}' generated"
                    f" no requests.\n",
                )

            for req in requests:
                req_stage_name = req.stage.__class__.__name__
                if self._insertion_policy(req):  # scheduler policy decides
                    queue.append(req.stage)
                    logger.info(
                        f"\n[Scheduler] Request {req} approved → Stage '"
                        f"{req_stage_name}' appended to queue.\n",
                    )
                else:
                    logger.info(
                        f"\n[Scheduler] Request {req} rejected → Stage':"
                        f"{req_stage_name}' not appended.\n",
                    )

            step += 1

        logger.info(
            f"\n{'=' * 30}\n[Scheduler] Pipeline completed.\n"
            f"Final sample metadata: {_sample.__dict__}\n"
            f"Final scheduler, metadata: {self._metadata}\n{'=' * 30}\n",
        )
        return _sample

    def handle_metadata_request(
        self,
        _metadata: TAbstractStageMetadata[TMetadataSchemaDict, TMetadataKeys],
    ) -> None:
        """Update scheduler metadata based on new stage metadata.

        This method merges peak and processing information from a
        stage's metadata into the scheduler's global metadata
        record.

        Parameters
        ----------
        new_scheduler_metadata : AbstractSchedulerMetadata
            Metadata produced by a stage to update the scheduler
            state.
        """
        if not _metadata.unwrap():
            return

        curr_peak = _metadata.unwrap().get(
            "current_peak_index",
            -1,
        )

        if curr_peak == -1:
            return

        if not self._metadata.unwrap():
            self._metadata = SchedulerMetadata(
                {
                    ESchedulerMetadataDictKeys.PROCESSED.value: 1,
                },
            )
        else:
            processed = self._metadata[ESchedulerMetadataDictKeys.PROCESSED]
            self._metadata[ESchedulerMetadataDictKeys.PROCESSED] = (
                processed + 1
            )

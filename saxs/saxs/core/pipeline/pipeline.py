"""pipeline.py.

This module defines the `Pipeline` class, which manages the dynamic
execution of SAXS (Small-Angle X-ray Scattering) processing stages.
A `Pipeline` coordinates a set of `AbstractStage` objects and
executes them using a provided scheduler. Stages can generate
additional stages at runtime, and their inclusion is governed by
the scheduler's insertion policy.

Classes
--------
Pipeline
    Manages execution of a sequence of stages using a scheduler.
"""

from saxs.saxs.core.pipeline.scheduler.scheduler import (
    AbstractScheduler,
)
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.flow_metadata import FlowMetadata
from saxs.saxs.core.types.sample import SAXSSample


class Pipeline:
    """
    Manages the dynamic execution of SAXS processing stages.

    A `Pipeline` coordinates a list of `AbstractStage` instances and
    executes them using a given `AbstractScheduler`. The scheduler
    determines the execution order and decides whether new stages
    requested by existing stages should be added to the queue based
    on its insertion policy.

    Attributes
    ----------
    init_stages : list of AbstractStage
        List of initial stages to execute in the pipeline.
    scheduler : AbstractScheduler
        Scheduler responsible for controlling stage execution and
        handling insertion policies.
    """

    def __init__(
        self,
        init_stages: list[IAbstractStage],
        scheduler: AbstractScheduler,
    ):
        """Initialize the pipeline with stages and a scheduler.

        Parameters
        ----------
        init_stages : list of AbstractStage
            Initial list of stages to include in the pipeline.
        scheduler : AbstractScheduler
            Scheduler instance that manages stage execution and
            insertion logic.
        """
        self.init_stages = init_stages or []
        self.scheduler = scheduler

    @classmethod
    def with_stages(
        cls,
        stages: list[IAbstractStage],
        scheduler: AbstractScheduler,
    ) -> "Pipeline":
        """Class method to create a pipeline with initial stages.

        Create a new pipeline with the specified stages and
        scheduler.

        Parameters
        ----------
        stages : list of AbstractStage
            List of stages to initialize the pipeline with.
        scheduler : AbstractScheduler
            Scheduler that will manage execution and insertion
            of stages.

        Returns
        -------
        Pipeline
            A configured pipeline instance with the given stages
            and scheduler.
        """
        return cls(
            init_stages=list(stages),
            scheduler=scheduler,
        )

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the pipeline on the provided sample.

        Enqueues the initial stages into the scheduler, then
        delegates execution to the scheduler's `run` method.

        Parameters
        ----------
        init_sample : SAXSSample
            The initial sample object to be processed through all
            pipeline stages.

        Returns
        -------
        SAXSSample
            The final processed sample after all stages in the
            pipeline have completed.
        """
        self.scheduler.enqueue_initial_stages(self.init_stages)

        return self.scheduler.run(
            init_sample=init_sample,
            init_flow_metadata=FlowMetadata(
                value={},
            ),  # defaut dict without name
        )

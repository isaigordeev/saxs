"""Pipeline: manages dynamic execution of processing stages."""

from saxs.core.pipeline.scheduler.scheduler import IAbstractScheduler
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample


class Pipeline:
    """Coordinates stage execution using a scheduler.

    Attributes
    ----------
    init_stages : list[IAbstractStage]
        Initial stages to execute.
    scheduler : IAbstractScheduler
        Scheduler controlling execution order.
    """

    def __init__(
        self,
        init_stages: list[IAbstractStage],
        scheduler: IAbstractScheduler,
    ):
        self.init_stages = init_stages or []
        self.scheduler = scheduler

    @classmethod
    def with_stages(
        cls,
        stages: list[IAbstractStage],
        scheduler: IAbstractScheduler,
    ) -> "Pipeline":
        """Create a pipeline with initial stages."""
        return cls(init_stages=list(stages), scheduler=scheduler)

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the pipeline on the provided sample."""
        self.scheduler.enqueue_initial_stages(self.init_stages)
        return self.scheduler.run(
            init_sample=init_sample,
            init_flow_metadata=FlowMetadata(),
        )

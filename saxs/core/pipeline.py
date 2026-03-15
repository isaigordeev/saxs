"""Pipeline: manages dynamic execution of processing stages."""

from saxs.core.scheduler import IAbstractScheduler
from saxs.core.stage import IAbstractStage
from saxs.core.types import FlowMetadata, SAXSSample


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


__all__ = ["Pipeline"]

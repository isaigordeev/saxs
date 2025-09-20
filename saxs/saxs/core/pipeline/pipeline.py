#
# Created by Isai GORDEEV on 19/09/2025.
#

from typing import List, Optional

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.scheduler.scheduler import (
    AbstractScheduler,
    BaseScheduler,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage


class Pipeline:
    """
    Manages dynamic execution of stages.
    Stages can request additional stages, and the Scheduler decides the
    insertion policy.
    """

    def __init__(
        self,
        init_stages: Optional[List[AbstractStage]] = None,
        scheduler: Optional[AbstractScheduler] = None,
    ):
        self.init_stages = init_stages or []
        self.scheduler = scheduler or BaseScheduler(self.init_stages)

    @classmethod
    def with_stages(
        cls,
        *stages: AbstractStage,
        scheduler: Optional[AbstractScheduler] = None,
    ) -> "Pipeline":
        """Convenience constructor to create a Pipeline with given stages."""
        return cls(init_stages=list(stages), scheduler=scheduler)

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        return self.scheduler.run(init_sample)

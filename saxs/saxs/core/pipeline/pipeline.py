#
# Created by Isai GORDEEV on 19/09/2025.
#

from typing import List, Optional, Type

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    InsertionPolicy,
    SaturationInsertPolicy,
)
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
        scheduler: Optional[Type[AbstractScheduler]] = None,
        scheduler_policy: Optional[Type[InsertionPolicy]] = None,
    ):
        self.policy = scheduler_policy or SaturationInsertPolicy()
        self.init_stages = init_stages or []
        self.scheduler = scheduler or BaseScheduler

    @classmethod
    def with_stages(
        cls,
        *stages: AbstractStage,
        scheduler: Optional[Type[AbstractScheduler]] = None,
        scheduler_policy: Optional[Type[InsertionPolicy]] = None,
    ) -> "Pipeline":
        """Creation of pipeline with given stages."""
        return cls(
            init_stages=list(stages),
            scheduler=scheduler,
            scheduler_policy=scheduler_policy,
        )

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        _instance = self.scheduler(self.init_stages, self.policy)
        return _instance.run(init_sample)

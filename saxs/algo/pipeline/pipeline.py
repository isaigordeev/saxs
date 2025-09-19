#
# Created by Isai GORDEEV on 19/09/2025.
#

from collections import deque
from typing import List, Optional

from saxs.algo.data.sample import SAXSSample
from saxs.algo.pipeline.scheduler.scheduler import (
    AbstractScheduler,
    SimpleScheduler,
    StageRequest,
)
from saxs.algo.pipeline.stage.abstract_stage import AbstractStage


class Pipeline:
    """
    Manages dynamic execution of stages.
    Stages can request additional stages, and Scheduler decides the insertion policy.
    """

    def __init__(
        self,
        init_stages: Optional[List["AbstractStage"]] = None,
        scheduler: AbstractScheduler = SimpleScheduler,
    ):
        self.scheduler = scheduler

    def add_stage(self, stage: "AbstractStage"):
        self.init_stages.append(stage)
        return self

    def run(self, init_sample: "SAXSSample") -> "SAXSSample":
        sample = self.scheduler.run(init_sample)

        return sample

#
# Created by Isai GORDEEV on 20/09/2025.
#
from abc import ABC, abstractmethod
from collections import deque
from typing import List, Optional

from saxs.saxs.core.pipeline.scheduler.insertion_policy import (
    AlwaysInsertPolicy,
    InsertionPolicy,
)
from saxs.saxs.core.pipeline.scheduler.stage_request import StageRequest


class AbstractScheduler(ABC):
    """Abstract base class for all schedulers."""

    def __init__(
        self,
        init_stages: Optional[List] = None,
        insertion_policy: Optional[InsertionPolicy] = None,
    ):
        self._queue = deque(init_stages or [])
        self._insertion_policy = insertion_policy or AlwaysInsertPolicy()

    @abstractmethod
    def run(self, init_sample):
        pass


class BaseScheduler(AbstractScheduler):
    """Executes stages sequentially and appends new requests to the end of the
    queue."""

    def run(self, init_sample):
        queue = deque(self._queue)
        sample = init_sample

        while queue:
            stage = queue.popleft()
            sample = stage.process(sample)

            # collect new stage requests
            requests: List[StageRequest] = stage.get_next_stage()

            for req in requests:
                if self._insertion_policy(req):  # <- policy decides
                    queue.append(req.stage)

        return sample

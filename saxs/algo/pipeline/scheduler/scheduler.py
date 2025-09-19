#
# Created by Isai GORDEEV on 20/09/2025.
#


from collections import deque
from typing import Callable, List

from saxs.algo.pipeline.scheduler.stage_request import StageRequest


class AbstractScheduler:
    """Abstract Scheduler"""

    _insertion_policy: Callable[..., bool]
    _queue = deque()

    def __init__(self, init_stages):
        self._queue = deque(init_stages or [])


class SimpleScheduler:
    def __init__(self, init_stages):
        super().__init__(init_stages)

    def run(self, init_sample):
        queue = deque(self._queue)
        sample = init_sample

        while queue:
            stage = queue.popleft()

            # Process the sample
            sample = stage.process(sample)

            # Get additional stages from the current stage
            requests: List[StageRequest] = stage.get_additional_stages()

            # Scheduler decides where to insert them
            for req in requests:
                # Policy: insert at end of queue
                queue.append(req.stage)

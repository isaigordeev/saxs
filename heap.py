from saxs.saxs.processing.kernel.simple_kernel import SimpleKernel
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    SaturationInsertPolicy,
)

scheduler_policy = SaturationInsertPolicy()
scheduler = BaseScheduler(insertion_policy=scheduler_policy)
kernel = SimpleKernel(scheduler=scheduler)

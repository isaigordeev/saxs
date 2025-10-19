from saxs.saxs.core.data.reader import DataReader
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    SaturationInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.processing.kernel.simple_kernel import SimpleKernel

data_reader = DataReader("tests/test_processing_data/075775_treated_xye.csv")
scheduler_policy = SaturationInsertPolicy()
scheduler = BaseScheduler(insertion_policy=scheduler_policy)
kernel = SimpleKernel(scheduler=scheduler)

q, i, di = data_reader.read_data()
_sample = data_reader.create_sample(q, i, di)
print(_sample)
_ = kernel.run(_sample)

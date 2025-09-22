import pytest

from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    SaturationInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.processing.kernels.simple_kernel import SimpleKernel

# ------------------------
# Semi-real fixtures
# ------------------------


@pytest.fixture
def init_sample():
    from saxs.saxs.core.data.sample import SAXSSample
    from saxs.saxs.core.data.sample_objects import (
        AbstractSampleMetadata,
        Intensity,
        IntensityError,
        QValues,
    )

    q = QValues([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    i = Intensity([1.0, 2.0, 3.0, 9.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    err = IntensityError(
        [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    )

    meta = AbstractSampleMetadata({"source": "test"})
    return SAXSSample(
        q_values=q, intensity=i, intensity_error=err, metadata=meta
    )


class TestSimpleKernel:
    """Test cases for Pipeline class using fixtures."""

    def test_simple_kernel_run(self, init_sample):
        kernel = SimpleKernel(
            scheduler=BaseScheduler, scheduler_policy=SaturationInsertPolicy()
        )
        kernel.build_pipeline()
        sample = init_sample
        # run kernel
        kernel.run(sample)

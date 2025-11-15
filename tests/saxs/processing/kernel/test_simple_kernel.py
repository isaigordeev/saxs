import os

import numpy as np
import pandas as pd
import pytest
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    SaturationInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.processing.kernel.simple_kernel import SimpleKernel


def read_data(data_dir_file):
    _data_name_dir, extension = os.path.splitext(data_dir_file)

    if extension == ".csv":
        data = pd.read_csv(data_dir_file, sep=",")
        data = data.apply(pd.to_numeric, errors="coerce")
        data = data.dropna()
        if data.shape[1] >= 3:
            q = np.array(data.iloc[:, 0])
            i = np.array(data.iloc[:, 1])
            di = np.array(data.iloc[:, 2])
            return q, i, di
        if data.shape[1] == 2:
            q = np.array(data.iloc[:, 0])
            i = np.array(data.iloc[:, 1])
            return q, i, None
    return None


# ------------------------
# Semi-real fixtures
# ------------------------


@pytest.fixture
def real_sample():
    from saxs.saxs.core.types.sample import SAXSSample
    from saxs.saxs.core.types.sample_objects import (
        Intensity,
        IntensityError,
        QValues,
        SampleMetadata,
    )

    q, i, err = read_data("tests/test_processing_data/075775_treated_xye.csv")

    delta_q = (q[np.size(q) - 1] - q[0]) / np.size(q)

    q = QValues(q)
    i = Intensity(i)
    err = IntensityError(err)

    meta = SampleMetadata(
        {"delta_q": delta_q, "max_intensity": max(i.unwrap())},
    )
    return SAXSSample(
        q_values=q,
        intensity=i,
        intensity_error=err,
        metadata=meta,
    )


@pytest.fixture
def init_sample():
    from saxs.saxs.core.types.sample import SAXSSample
    from saxs.saxs.core.types.sample_objects import (
        Intensity,
        IntensityError,
        QValues,
        SampleMetadata,
    )

    q = QValues([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    i = Intensity([1.0, 2.0, 3.0, 9.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    err = IntensityError(
        [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
    )

    meta = SampleMetadata(
        {"delta_q": 0.01, "max_intensity": max(i.unwrap())},
    )
    return SAXSSample(
        q_values=q,
        intensity=i,
        intensity_error=err,
        metadata=meta,
    )


class TestSimpleKernel:
    """Test cases for Pipeline class using fixtures."""

    # def test_simple_kernel_run(self, init_sample):
    #     kernel = SimpleKernel(
    #         scheduler=BaseScheduler, scheduler_policy=SaturationInsertPolicy()
    #     )
    #     kernel.build_pipeline()
    #     sample = init_sample
    #     # run kernel
    #     kernel.run(sample)

    def test_simple_kernel_run_with_real_sample(self, real_sample) -> None:
        kernel = SimpleKernel(
            scheduler=BaseScheduler,
            scheduler_policy=SaturationInsertPolicy(15),
        )
        kernel.build_pipeline()
        sample = real_sample
        # run kernel
        kernel.run(sample)

    # def test_old_run_with_real_sample(self):
    #     a = Manager(
    #         peak_data_path="tests/test_processing_data",
    #         peak_kernel=RobustParabolePeakKernel,
    #         # phase_kernel=DefaultPhaseKernel,
    #     )
    #     a()

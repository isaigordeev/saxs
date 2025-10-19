from saxs.application.manager import Manager
from saxs.saxs.peak.parabole_kernel import (
    RobustParabolePeakKernel,
)
from saxs.saxs.phase.default_kernel import DefaultPhaseKernel


def test_manager_runs_without_error():
    """
    Test that the Manager runs the processing pipeline.

    This test ensures that the pipeline completes all
    processing steps without raising any exceptions or
    crashing.
    """
    manager = Manager(
        peak_data_path="tests/test_processing_data",
        peak_kernel=RobustParabolePeakKernel,
        phase_kernel=DefaultPhaseKernel,
    )

    # Call the processing pipeline
    manager_instance = manager()
    # Check that result is a dictionary (based on AbstractPeakKernel.gat
    # hering)

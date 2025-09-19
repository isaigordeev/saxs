from saxs.algo.manager import Manager
from saxs.algo.peak.parabole_kernel import (
    RobustParabolePeakKernel,
)
from saxs.algo.phase.default_kernel import DefaultPhaseKernel


def test_manager_runs_without_error():
    """
    Test that the Manager runs the processing pipeline without crashing.
    """

    # Initialize Manager
    manager = Manager(
        peak_data_path="tests/test_processing_data",
        peak_kernel=RobustParabolePeakKernel,
        phase_kernel=DefaultPhaseKernel,
    )

    # Call the processing pipeline
    manager_instance = manager()

    # Check that result is a dictionary (based on AbstractPeakKernel.gathering)
    # assert manager.peak_application_instance.kernel == 2

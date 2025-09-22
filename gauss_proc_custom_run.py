from saxs.application.manager import Manager

from saxs.saxs.peak.parabole_kernel import (
    RobustParabolePeakKernel,
)
from saxs.saxs.phase.default_kernel import DefaultPhaseKernel

# a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data/075775_treated_xye.csv')

# a = PeakApplication('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data', ParabolePeakKernel)
# a.peak_classification()

# b = PhaseApplication('/Users/isaigordeev/Desktop/2023/saxs/results/session_results/2023-07-28/22:57:00_prominence_kernel.json', AbstractPhaseKernel)
# b.phase_classification()

# a = Manager(peak_kernel=ParabolePeakKernel, phase_kernel=DefaultPhaseKernel)
a = Manager(
    peak_data_path="tests/test_processing_data",
    peak_kernel=RobustParabolePeakKernel,
    phase_kernel=DefaultPhaseKernel,
)
# a = Manager(peak_data_directory='res/', peak_kernel=RobustParabolePeakKernel, phase_kernel=DefaultPhaseKernel)

# a = Manager(peak_kernel=ProminencePeakKernel, phase_kernel=DefaultPhaseKernel)
a()

# if __main__ == '__main__'
# a()
# test.directory_processing()

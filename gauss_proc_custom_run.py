from datetime import datetime

from saxs.gaussian_processing.peak.peak_application import PeakApplication
from saxs.gaussian_processing.phase.phase_application import PhaseApplication

from saxs.gaussian_processing.peak.prominence_kernel import ProminenceKernel
from saxs.gaussian_processing.peak.parabole_kernel import ParabolePeakKernel
from saxs.gaussian_processing.phase.phase_classificator import AbstractPhaseKernel

# a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data/075775_treated_xye.csv')

a = PeakApplication('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data', ParabolePeakKernel)
a.peak_classification()

b = PhaseApplication('/Users/isaigordeev/Desktop/2023/saxs/results/session_results/2023-07-28/22:57:00_prominence_kernel.json', AbstractPhaseKernel)
b.phase_classification()

# test = Manager(peak_classificator=ProminencePeakClassificator,
#                phase_classificator=None,)


# test.directory_processing()



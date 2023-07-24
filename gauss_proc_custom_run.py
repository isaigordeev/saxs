from datetime import datetime

from saxs.gaussian_processing.peak.peak_application import PeakApplication
from saxs.gaussian_processing.peak.prominence_kernel import ProminenceKernel
from saxs.gaussian_processing.peak.parabole_kernel import ParabolePeakKernel


# a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data/075775_treated_xye.csv')

a = PeakApplication('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data', ParabolePeakKernel)
a.directory_classification()

# test = Manager(peak_classificator=ProminencePeakClassificator,
#                phase_classificator=None,)


# test.directory_processing()



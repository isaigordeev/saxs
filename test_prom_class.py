from datetime import datetime

from saxs.gaussian_processing.peak.peak_application import PeakApplication
from saxs.gaussian_processing.peak.prom_peak_classificator import ProminenceKernel

now = datetime.now()


# a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/data/075775_treated_xye.csv')

a = PeakApplication('/Users/isaigordeev/Desktop/2023/saxs/data/', ProminenceKernel)
a.directory_classification()

# test = Manager(peak_classificator=ProminencePeakClassificator,
#                phase_classificator=None,)


# test.directory_processing()



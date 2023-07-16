from datetime import datetime

from saxs.gaussian_processing.peak.prom_peak_classificator import ProminenceKernel

now = datetime.now()


a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/data/075773_treated_xye.csv')

# test = Manager(peak_classificator=ProminencePeakClassificator,
#                phase_classificator=None,)


# test.directory_processing()



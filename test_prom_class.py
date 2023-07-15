from datetime import datetime

from saxs.gaussian_processing.prom_peak_classificator import ProminencePeakClassificator
from saxs.gaussian_processing.manager import Manager

now = datetime.now()

test = Manager(peak_classificator=ProminencePeakClassificator,
               phase_classificator=None,)


test.directory_processing()



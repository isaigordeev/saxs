from datetime import datetime

from saxs.gaussian_processing.p_peak_classification import PDefaultPeakClassificator
from saxs.gaussian_processing.phase_classificator import DefaultPhaseClassificator
from saxs.gaussian_processing.manager import Manager

now = datetime.now()

 
test = Manager(current_session=now,
               peak_classificator=PDefaultPeakClassificator,
               phase_classificator=DefaultPhaseClassificator,
               )
test.directory_peak_processing()


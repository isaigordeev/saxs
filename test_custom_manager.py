from datetime import datetime

from saxs.gaussian_processing.p_peak_classification import PDefaultPeakClassificator, DefaultPeakClassificator
from saxs.gaussian_processing.phase_classificator import DefaultPhaseClassificator
from saxs.gaussian_processing.manager import Manager

now = datetime.now()

 
test = Manager(current_session=now,
               peak_classificator=DefaultPeakClassificator,
               phase_classificator=DefaultPhaseClassificator,
               )

test.custom_directory_process()


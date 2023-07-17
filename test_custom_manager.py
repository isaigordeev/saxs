from datetime import datetime

from saxs.gaussian_processing.peak.p_peak_classification import DefaultPeakApplication
from saxs.gaussian_processing.phase.phase_classificator import DefaultPhaseApplication
from saxs.gaussian_processing.manager import Manager

now = datetime.now()

 
test = Manager(current_session=now,
               peak_classificator=DefaultPeakApplication,
               phase_classificator=DefaultPhaseApplication,
               )

test.custom_directory_processing()


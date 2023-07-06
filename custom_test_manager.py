from manager import *
from saxs_processing.p_peak_classification import PDefaultPeakClassificator
from saxs_processing.phase_classificator import DefaultPhaseClassificator

now = datetime.now()

 
test = Custom_Manager(current_session=now,
                      peak_classificator=PDefaultPeakClassificator,
                      phase_classificator=DefaultPhaseClassificator,
                      peak_data_directory='data_test/',
                      phase_data_directory=ANALYSE_DIR_SESSIONS_RESULTS,
                      )
test.directory_processing()


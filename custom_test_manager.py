from manager import *
from saxs_processing.p_peak_classification import PDefaultPeakClassificator
from datetime import datetime

now = datetime.now()


test = Custom_Manager(_class=PDefaultPeakClassificator, current_session=now)
test.repo_processing()


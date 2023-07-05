from manager import *
from saxs_processing.p_peak_classification import PPeaks
from datetime import datetime

now = datetime.now()


test = Custom_Manager(_class=PPeaks, current_session=now)
test.repo_processing()


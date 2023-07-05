from manager import *
from saxs_processing.p_peak_classification import PPeaks

test = Custom_Manager(_class=PPeaks, current_session='heap/')
test.repo_processing()


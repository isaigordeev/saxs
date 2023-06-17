from manager import *
from phase_processing.p_peak_classification import PPeaks

test = Manager('heap/', _class=PPeaks)
test.custom_repo_processing()


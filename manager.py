from peak_classification import *
from phase_classification import *

peaks = Peaks(q, I, dI)

peaks.background_reduction()
peaks.filtering_negative()
peaks.phase_classification()

# print('q', peaks.peaks_analysed_q)
# print('I', peaks.peaks_analysed_I)
# print(sorted(peaks.peaks_analysed_q) / min(peaks.peaks_analysed_q))
# print('sigma', sorted(peaks.peaks_analysed_b))

phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
phase.analyzing()
from peak_classification import *
# from phase_classification import *

peaks = Peaks(q, I, dI)

peaks.background_reduction()
peaks.filtering()
peaks.filtering_negative()
peaks.phase_classification()

print(peaks.peaks_analysed_q,)
print(peaks.peaks_analysed_I,)


# phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
# phase.analyzing()
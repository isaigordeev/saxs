import matplotlib.pyplot as plt

from processing.peak_classification import *
# from processing.phase_classification import *


peaks = Peaks(q, I, dI)
peaks.background_reduction()
peaks.filtering()
peaks.filtering_negative()
peaks.phase_classification()
peaks.plot_diagramme(0)
peaks.loss()

# print(peaks.peaks_analysed_q,)
# print(peaks.peaks_analysed_I,)
# plt.clf()
# plt.plot(peaks.peaks_analysed_q, peaks.peaks_analysed_I, 'x' )
# plt.show()

# phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
# phase.analyzing()
import matplotlib.pyplot as plt

from processing.peak_classification import *
# from processing.phase_classification import *


peaks = Peaks(FILENAME, DATA_DIR)
peaks.background_reduction()
peaks.filtering()
peaks.filtering_negative()
peaks.peak_processing()
peaks.gathering()
# print(peaks.peaks_plots)
peaks.result_plot()

# print(peaks.peaks_analysed_q,)
# print(peaks.peaks_analysed_I,)
# plt.clf()
# plt.plot(peaks.peaks_analysed_q, peaks.peaks_analysed_I, 'x' )
# plt.show()

# phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
# phase.analyzing()
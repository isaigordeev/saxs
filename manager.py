from processing.peak_classification import *
# from processing.phase_classification import *
from datetime import date, datetime
import time

today = date.today()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'


peaks = Peaks(FILENAME, DATA_DIR, current_session=current_session)
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
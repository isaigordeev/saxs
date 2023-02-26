import matplotlib.pyplot as plt

from processing.peak_classification import *
# from processing.phase_classification import *
import os

analyse_directory = './data_test/'

def get_filenames(folder_path):
    """
    Generator that yields the filenames in the given folder path.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            yield filename

for filename in get_filenames(analyse_directory):
    peaks = Peaks(filename, analyse_directory)
    peaks.background_reduction()
    peaks.filtering()
    peaks.filtering_negative()
    peaks.phase_classification()
    peaks.stage_plot(0)
    peaks.loss()
    peaks.result_plot()

# print(peaks.peaks_analysed_q,)
# print(peaks.peaks_analysed_I,)
# plt.clf()
# plt.plot(peaks.peaks_analysed_q, peaks.peaks_analysed_I, 'x' )
# plt.show()

# phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
# phase.analyzing()
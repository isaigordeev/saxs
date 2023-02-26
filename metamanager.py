import matplotlib.pyplot as plt

from processing.peak_classification import *
# from processing.phase_classification import *
import os


def get_filenames(folder_path):
    """
    Generator that yields the filenames in the given folder path.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            yield filename


def get_filenames_without_ext(folder_path):
    """
    Generator that yields the filenames (without extensions) in the given folder path.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Split the filename into name and extension, and return just the name
            name, extension = os.path.splitext(filename)
            yield name


for filename in get_filenames_without_ext(DATA_DIR):
    peaks = Peaks(filename, DATA_DIR)
    peaks.background_reduction()
    peaks.filtering()
    peaks.background_plot()
    peaks.filtering_negative()
    peaks.phase_classification()
    peaks.loss()
    peaks.result_plot()

# print(peaks.peaks_analysed_q,)
# print(peaks.peaks_analysed_I,)
# plt.clf()
# plt.plot(peaks.peaks_analysed_q, peaks.peaks_analysed_I, 'x' )
# plt.show()

# phase = Phase(peaks.peaks_analysed_q, peaks.peaks_analysed_I, dI)
# phase.analyzing()

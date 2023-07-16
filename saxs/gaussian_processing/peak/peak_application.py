import json
import os
from abc import ABC

import numpy as np
import pandas as pd

from saxs.gaussian_processing.peak.abstract_kernel import AbstractPeakKernel
from saxs.gaussian_processing.processing_classificator import ApplicationClassificator
from saxs.gaussian_processing.processing_outils import get_filenames, get_filenames_without_ext
from saxs.gaussian_processing.settings_processing import EXTENSION, ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS




class PeakApplication(ApplicationClassificator):

    def __init__(self, data_directory, kernel: AbstractPeakKernel=None):
        super().__init__(data_directory)

        self.kernel = kernel
        self.file_analyse_dir_peaks = None
        self.file_analyse_dir = None
        self.samples = get_filenames_without_ext(self.data_directory)


    def set_output_peak_directories(self, filename):  # TODO MAKE STATIC
        print(self._results_dir)
        self.file_analyse_dir = os.path.join(self._result_plots_dir, filename)
        self.file_analyse_dir_peaks = os.path.join(self.file_analyse_dir, 'peaks')

        print(self.file_analyse_dir)
        print(self.file_analyse_dir_peaks)

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)



    def write_peaks_data(self):  # TODO MAKE STATIC

        # with open('{}.json'.format(self._current_results_dir_session), 'r') as f:
        #     directory_data = json.load(f)
        with open('{}{}_{}.json'.format(self._current_results_dir_session, self.current_time, self.kernel.class_info()), 'w') as f:
            json.dump(self.data, f, indent=4, separators=(",", ": "))

    def directory_classification(self):
        for sample_name, sample_ext in self.samples:
            sample = '{}{}'.format(sample_name, sample_ext)
            self.set_output_peak_directories(sample)
            self.data[sample] = self.kernel(os.path.join(self.data_directory, sample))()

        self.write_peaks_data()

    def background_reduction(self):
        pass

    def filtering(self):
        pass

    def peak_searching(self, height, distance, prominence):
        pass

    def peak_fitting(self, i, width_factor):
        pass

    def peak_processing(self):
        pass

    def gathering(self):
        pass

    def sum_total_fit(self):
        pass

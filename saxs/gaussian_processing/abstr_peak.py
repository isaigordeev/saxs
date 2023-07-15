import json
import os
from abc import ABC

import numpy as np
import pandas as pd

from .processing_classificator import ApplicationClassificator
from .settings_processing import EXTENSION, ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS


class AbstractPeakClassificator(ApplicationClassificator):
    # __data = {}
    # def __new__(cls, *args, **kwargs):
    #     _peak_class_dir_instance = super().__new__(cls)
    #     return _peak_class_dir_instance

    # @classmethod
    # def write_data(cls):
    #
    #     with open('{}.json'.format(cls.current_results_dir_session), 'r') as file:
    #         directory_data = json.load(file)
    #
    #     with open(cls.current_results_dir_session + cls.current_time + '.json', 'w') as f:
    #         json.dump(directory_data, f, indent=4, separators=(",", ": "))

    def __init__(self, data_directory):
        super().__init__(data_directory)


        self.file_analyse_dir_peaks = None
        self.file_analyse_dir = None
        self.I_raw = None
        self.dI = None
        self.q = None

        self.delta_q = None
        self.max_dI = None


    def set_file_peak_directories(self, filename):
        print(self._analysis_dir)
        self.file_analyse_dir = os.path.join(self._analysis_dir, filename)
        self.file_analyse_dir_peaks = os.path.join(self.file_analyse_dir, 'peaks')

        print(self.file_analyse_dir)
        print(self.file_analyse_dir_peaks)

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)

    def set_file_data(self, filename):
        data = pd.read_csv('{}{}{}'.format(self.data_directory, filename, EXTENSION), sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I_raw = np.array(data.iloc[:, 1])
        # self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.max(self.dI)

    def write_file_data(self):

        with open('{}.json'.format(self._current_results_dir_session), 'r') as file:
            directory_data = json.load(file)

        directory_data.update({self.filename: self.gathering()})

        with open(self._current_results_dir_session + self.current_time + '.json', 'w') as f:
            json.dump(directory_data, f, indent=4, separators=(",", ": "))

    def directory_classification(self, sample_names=None):
        pass

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

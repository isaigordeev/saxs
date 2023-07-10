import json
import os
from abc import ABC

import numpy as np
import pandas as pd

from .processing_classificator import ApplicationClassificator
from .settings_processing import EXTENSION, ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS


class AbstractPeakClassificator(ApplicationClassificator):

    def __init__(self, current_session, data_directory, filename, custom_directory=None):
        super().__init__(current_session, data_directory)

        self.file_analyse_dir_peaks = None
        self.file_analyse_dir = None
        self.max_dI = None
        self.delta_q = None
        self.dI = None
        self.I = None
        self.q = None

        self.filename = filename
        self.data_directory = data_directory
        self.custom_directory = custom_directory

        self.set_peak_directories()
        self.set_data()

    def set_peak_directories(self):
        if self.custom_directory is None:
            print(self.analysis_dir)
            self.file_analyse_dir = os.path.join(self.analysis_dir, self.filename)
            self.file_analyse_dir_peaks = os.path.join(self.file_analyse_dir, 'peaks')
        else:
            self.file_analyse_dir = self.custom_directory + self.filename
            self.file_analyse_dir_peaks = self.custom_directory + self.filename + 'peaks'

        print(self.file_analyse_dir)
        print(self.file_analyse_dir_peaks)

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)

    def set_data(self):
        data = pd.read_csv('{}{}{}'.format(self.data_directory, self.filename, EXTENSION), sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        # self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        # self.max_dI = np.median(self.dI)

    def write_data(self):

        with open('{}.json'.format(self.current_session_results), 'r') as file:
            directory_data = json.load(file)

        directory_data.update({self.filename: self.gathering()})

        with open(self.current_session_results + self.current_time + '.json', 'w') as f:
            json.dump(directory_data, f, indent=4, separators=(",", ": "))

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

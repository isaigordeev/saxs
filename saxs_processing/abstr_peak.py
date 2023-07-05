import json
import os

import numpy as np
import pandas as pd

from settings_processing import EXTENSION, ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS


class PeakClassificator:

    def __init__(self, filename, DATA_DIR, current_session, custom_directory=None):
        self.file_analyse_dir_peaks = None
        self.file_analyse_dir = None
        self.max_dI = None
        self.delta_q = None
        self.dI = None
        self.I = None
        self.q = None
        self.custom_directory = custom_directory
        self.filename = filename
        self.DATA_DIR = DATA_DIR
        self.current_date_session = str(current_session.today().date()) + '/'
        self.current_time = current_session.strftime("%H:%M:%S")

        self.set_directories()
        self.set_data()




    def set_directories(self):
        if self.custom_directory is None:
            self.file_analyse_dir = ANALYSE_DIR_SESSIONS + self.filename
            self.file_analyse_dir_peaks = ANALYSE_DIR_SESSIONS + self.filename + '/peaks'
        else:
            self.file_analyse_dir = self.custom_directory + self.filename
            self.file_analyse_dir_peaks = self.custom_directory + self.filename + '/peaks'

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)

    def set_data(self):
        data = pd.read_csv(self.DATA_DIR + self.filename + EXTENSION, sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.median(self.dI)

    def write_data(self):

        current_session_results = ANALYSE_DIR_SESSIONS_RESULTS + self.current_date_session

        with open(current_session_results + self.current_time + '.json', 'w') as f:
            json.dump(self.gathering(), f, indent=4, separators=(",", ": "))

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

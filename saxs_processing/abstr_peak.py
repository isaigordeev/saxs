import os

import numpy as np
import pandas as pd

from settings_processing import EXTENSION


class PeakClassificator:
    
    def __init__(self, filename, DATA_DIR, current_session):
        self.filename = filename
        self.DATA_DIR = DATA_DIR
        self.current_session = current_session

        self.file_analyse_dir = current_session + self.filename
        self.file_analyse_dir_peaks = current_session + self.filename + '/peaks'

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)

        data = pd.read_csv(self.DATA_DIR + self.filename + EXTENSION, sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.median(self.dI)

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





import json
import os
from datetime import date, datetime
from abc import abstractmethod, ABC


# from fastdtw import fastdtw
import matplotlib.pyplot as plt
import torch
from torch import nn

from saxs_processing.processing_classificator import ProcessingClassificator
from settings_processing import *


today = date.today()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")


def ratio(data: np.array) -> np.array:
    for i in range(len(data) - 1):
        data[i] = data[i + 1] / data[i]
    return data


def ratio_data(i, data: np.array) -> np.array:
    return (data / data[i])[1:]


class AbstractPhaseClassificator(ProcessingClassificator):
    __slots__ = ('phases', 'phases_coefficients', 'phases_directory', 'filename_analyse_dir_phases')
    def __init__(self, data_directory, current_session, phases_directory=PHASES_DIR):
        super().__init__(data_directory, current_session)

        self.phases_directory = '../{}'.format(phases_directory)
        # self.set_directories()

        self.filename_analyse_dir_phases = ''
        self.phases_coefficients = ''
        self.phases = ''
        self.set_phases()



    def set_phases(self):
        with open(self.phases_directory, 'r') as file:  # NOTE make it better with string formatting
            self.phases = json.load(file)

        self.phases_coefficients = [[0] * len(x) for x in self.phases.values()]

        for i, phase in enumerate(self.phases.values()):
            phase = np.sqrt(phase)
            self.phases_coefficients[i] = ratio_data(0, phase)

        print(self.phases_coefficients)

    def set_directories(self):
        self.filename_analyse_dir_phases = ANALYSE_DIR_SESSIONS + self.current_data_session + 'phases'

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)

    def data_preparation(self):
        pass

    def loss(self, f, coeffs):
        pass

    def analyze(self):
        pass

    def gathering(self):
        pass

# a = AbstractPhaseClassificator(DATA_DIR, now)

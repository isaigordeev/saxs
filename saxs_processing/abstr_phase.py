import json
import os
from datetime import date, datetime

# from fastdtw import fastdtw
import matplotlib.pyplot as plt
import torch
from torch import nn

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


class Phases():
    def __init__(self, filename, current_session, phase_dir='phases'):

        self.q_normalized_ratio = np.array([])
        self.alignement_dict = {}
        self.DIR_PHASES = phase_dir

        with open(self.DIR_PHASES + '.json', 'r') as file:  # NOTE make it better with string formatting
            self.phases = json.load(file)

        self.phases_coefficients = [[0] * len(self.phases[x]) for x in range(len(self.phases))]

        self.filename = filename
        self.filename_analyse_dir = current_session + self.filename
        self.filename_analyse_dir_phases = current_session + self.filename + '/phases'

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)

        for i, phase in enumerate(self.phases.values()):
            phase = np.sqrt(phase)
            self.phases_coefficients[i] = ratio_data(0, phase)

        print(self.phases_coefficients)
    def data_preparation(self):
        pass

    def loss(self, f, coeffs):
        pass

    def analyze(self):
        pass

    def gathering(self):
        pass

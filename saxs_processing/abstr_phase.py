import json
import os
from datetime import date, datetime
from abc import abstractmethod, ABC


# from fastdtw import fastdtw
import matplotlib.pyplot as plt
import numpy as np
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
    __slots__ = ('phases',
                 'phases_coefficients',
                 'phases_directory',
                 'data',
                 'phases_number',
                 'phases_dict')
    def __init__(self, current_session, data_directory, phases_directory=PHASES_DIR):
        super().__init__(current_session, data_directory)

        self.phases_directory = '../{}'.format(phases_directory) #relative path

        self.phases_coefficients = np.array([])
        self.phases = {}
        self.data = {}
        self.phases_dict = {}
        self.phases_number = 0

        self.set_phases()


    def set_phases(self):
        with open(self.phases_directory, 'r') as file:  # NOTE make it better with string formatting
            self.phases = json.load(file)

        self.phases_coefficients = [[0] * len(x) for x in self.phases.values()]

        for i, phase in enumerate(self.phases.values()):
            phase = np.sqrt(phase)
            self.phases_coefficients[i] = ratio_data(0, phase)

        self.phases_number = len(self.phases.values())

        for i, phase in enumerate(self.phases.keys()):
            self.phases_dict[i] = phase

        print(self.phases_coefficients)
        print(self.phases_dict)

    def data_preparation(self):
        pass

    def loss(self, f, coeffs):
        pass

    def analyze(self):
        pass

    def gathering(self):
        pass


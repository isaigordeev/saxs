import os
from datetime import date, datetime

# from fastdtw import fastdtw
import matplotlib.pyplot as plt
import torch
from torch import nn

from settings import *

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
    def __init__(self, filename, current_session, phases, class_names, data: dict):

        self.q_normalized_ratio = np.array([])
        self.alignement_dict = {}
        self.phases = phases
        self.phases_coeffs = [[0] * len(self.phases[x]) for x in range(len(self.phases))]

        self.data = data
        self.q = np.array(data['q'])
        self.I = np.array(data['I'])

        self.q_analyzed = self.q
        self.I_analyzed = self.I

        self.I_raw = np.array(data['I_raw'])
        self.dI = data['dI']
        self.peaks = data['peaks']

        self.file = filename
        self.file_analyse_dir = current_session + self.file
        self.data_dir = DATA_DIR
        self.file_analyse_dir_phases = current_session + self.file + '/phases'

        if not os.path.exists(self.file_analyse_dir_phases):
            os.mkdir(self.file_analyse_dir_phases)

        self.zeros = np.zeros(len(self.q))
        self.peaks = list(map(int, self.peaks))
        self.q_normalized = np.array([])
        self.sorted_indices_I = []
        self.sorted_indices_I_start = []
        self.sorted_indices_q = []
        self.sorted_indices_q_start = []
        self.suspicious_peaks = 0

        self.class_names = class_names

        i = 0
        for x in self.phases:
            # print(ratio_data(0, x))
            self.phases_coeffs[i] = ratio_data(0, x)
            i += 1

    def preset_plot(self):
        plt.clf()
        # print(PROMINENCE, self.I / np.max(self.I))
        # print(self.ratio_data(np.array(self.q)))
        plt.plot(self.q, self.I, 'x', linewidth=0.5, label='data_without_background')
        plt.plot(self.q, self.I_raw, 'x', linewidth=0.5, label='raw_data_without_background')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir_phases + '/' + self.file + 'ratios_all_detected' + str(
                len(self.q_normalized_ratio) + 1) + '.pdf')

    def phase_plot(self):
        plt.clf()
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/phases_' + self.file + '.pdf')

    def treshhold_filtering(self):
        treshhold = 1.1 * PROMINENCE * np.average(self.I)
        errors = []

        for x in range(len(self.I)):
            if self.I[x] < treshhold:
                errors += [int(x)]

        self.q = np.delete(self.q, errors)
        self.I = np.delete(self.I, errors)
        print('Deleted: ', len(errors))

    def data_preparation(self):
        pass

    def loss(self, f, coeffs):
        pass

    def analyze(self):
        pass

    def gathering(self):
        pass
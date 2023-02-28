import numpy as np
from fastdtw import fastdtw
import matplotlib.pyplot as plt

from settings import *

from datetime import date, datetime
import time

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
    def __init__(self, filename, current_session, phases, data: dict):

        self.alignement_dict = {}
        self.phases = phases
        self.phases_coeffs = [[0] * len(self.phases[x]) for x in range(len(self.phases))]

        self.q = np.array(data['q'])
        self.I = np.array(data['I'])
        self.I_raw = np.array(data['I_raw'])
        self.dI = data['dI']
        self.peaks = data['peaks']

        self.file = filename
        self.zeros = np.zeros(len(self.q))
        self.file_analyse_dir = current_session + self.file
        self.peaks = list(map(int, self.peaks))
        self.q_normalized = np.array([])
        self.sorted_indices_I = []
        self.sorted_indices_q = []

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
        # plt.show()

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

    def data_preparing(self):
        self.sorted_indices_q = np.argsort(self.q)
        self.I = self.I[self.sorted_indices_q]
        self.q = self.q[self.sorted_indices_q]
        self.I_raw = self.I_raw[self.sorted_indices_q]
        self.sorted_indices_I = np.argsort(self.I)
        self.q_normalized = ratio_data(0, self.q)

        for x in range(len(self.phases_coeffs)):
            if len(self.q) < len(self.phases_coeffs[x]):
                self.phases_coeffs[x] = self.phases_coeffs[x][:len(self.q)-1]

        # print(self.phases_coeffs)

        # print(self.I, self.q, self.sorted_indices_q, self.sorted_indices_I)

    def score_func(self, f, coeffs):
        distance, path = f(coeffs, self.q,
                           dist=lambda x, y: abs(x - y))
        return distance, path

    def analyzing(self):
        self.alignement_dict[len(self.q)] = np.array([])
        for x in self.phases_coeffs:
            self.alignement_dict[len(self.q)] = np.append(self.alignement_dict[len(self.q)],
                                                          self.score_func(fastdtw, x))

        print(self.alignement_dict[len(self.q)][1])

    def alignement(self):
        fig = plt.figure(figsize=(12,12))
        for k in range(1, len(self.phases_coeffs)+1):
            fig.add_subplot(1, 3, k)
            plt.plot(self.q_normalized, label='x')
            plt.plot(self.phases_coeffs[k], label='y')
            for i, j in self.alignement_dict[len(self.q)][1]:
                plt.plot([i, j], [self.phases_coeffs[i], self.q[j]], color='gray')
            plt.legend()
            plt.show()

import os

import numpy as np
import torch
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from torch import nn

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

    def data_preparing(self):
        self.sorted_indices_I = np.argsort(self.I)
        self.sorted_indices_I_start = self.sorted_indices_I
        self.q_normalized_ratio = ratio_data(0, np.sqrt(self.q))

        for x in self.I:
            if x < 1.5 * PROMINENCE * np.average(self.I):
                self.suspicious_peaks += 1

        print('suspects ', self.suspicious_peaks)

        for x in range(len(self.phases_coeffs)):
            if len(self.q) < len(self.phases_coeffs[x]):
                self.phases_coeffs[x] = self.phases_coeffs[x][:len(self.q) - 1]

        # print(self.phases_coeffs)

        # print(self.I, self.q, self.sorted_indices_q, self.sorted_indices_I)

    def score_func(self, f, coeffs):
        distance, path = f(coeffs, self.q_analyzed,
                           dist=lambda x, y: abs(x - y))
        return distance, path

    def analyze(self):
        for x in self.phases_coeffs:
            self.alignement_dict[len(self.q_analyzed)] = np.append(self.alignement_dict[len(self.q_analyzed)],
                                                          self.score_func(fastdtw, x)[0])
        print(self.alignement_dict, 'dict')

    def gathering(self):
        softmin = nn.Softmin(dim=0)
        self.data['phase'] = self.class_names[np.argmin(self.alignement_dict[len(self.q)])]
        self.data['distribution'] = softmin(torch.tensor(self.alignement_dict[len(self.q)], dtype=torch.float32)).tolist()
        return self.data


class Fastdw(Phases):
    def __init__(self, filename, current_session, phases, class_names, data: dict):

        super().__init__(filename, current_session, phases, class_names, data)
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

    def data_preparing(self):
        self.sorted_indices_I = np.argsort(self.I)
        self.sorted_indices_I_start = self.sorted_indices_I
        self.q_normalized_ratio = ratio_data(0, np.sqrt(self.q))

        for x in self.I:
            if x < 1.5 * PROMINENCE * np.average(self.I):
                self.suspicious_peaks += 1

        print('suspects ', self.suspicious_peaks)

        for x in range(len(self.phases_coeffs)):
            if len(self.q) < len(self.phases_coeffs[x]):
                self.phases_coeffs[x] = self.phases_coeffs[x][:len(self.q) - 1]

        # print(self.phases_coeffs)

        # print(self.I, self.q, self.sorted_indices_q, self.sorted_indices_I)

    def score_func(self, f, coeffs):
        distance, path = f(coeffs, self.q_analyzed,
                           dist=lambda x, y: abs(x - y))
        return distance, path

    def analyze(self):
        self.alignement_dict[len(self.q_analyzed)] = np.array([])
        for x in self.phases_coeffs:
            self.alignement_dict[len(self.q_analyzed)] = np.append(self.alignement_dict[len(self.q_analyzed)],
                                                          self.score_func(fastdtw, x)[0])
        print(self.alignement_dict, 'dict')

    def reduction(self):
        self.q_normalized_ratio = np.delete(self.q_normalized_ratio, self.sorted_indices_I[0] - 1)

        self.I_analyzed = np.delete(self.I_analyzed, self.sorted_indices_I[0])
        self.q_analyzed = np.delete(self.q_analyzed, self.sorted_indices_I[0])
        for i in range(len(self.sorted_indices_I)):
            if self.sorted_indices_I[i] > self.sorted_indices_I[0]:
                self.sorted_indices_I[i] -= 1

        self.sorted_indices_I = np.delete(self.sorted_indices_I, [0])

    def alignement(self):
        fig = plt.figure(figsize=(12, 12))
        self.analyze()
        for i in range(self.suspicious_peaks):
            self.analyze()
            plt.clf()
            for k in range(1, len(self.phases_coeffs) + 1):
                plt.subplot(1, len(self.phases_coeffs), k)
                plt.plot(self.q_normalized_ratio, 'x', label='q_norm')
                plt.plot(self.q_normalized_ratio, label='q_norm')
                plt.plot(self.phases_coeffs[k - 1], label='coef ' + self.class_names[k - 1])
                plt.plot(self.phases_coeffs[k - 1], 'x', label='coef ' + self.class_names[k - 1])
                plt.title(self.class_names[k - 1] + f'peak_nums: {len(self.q_normalized_ratio)}')
                plt.legend()
                plt.xlabel('peak_number')
                plt.ylabel('ratio')
                plt.suptitle(f'The phase is {self.class_names[np.argmin(self.alignement_dict[len(self.q_analyzed)])]} with \
                 {np.min(self.alignement_dict[len(self.q_analyzed)])} diff dist')
                # for i, j in self.alignement_dict[len(self.q)][1]:
                #     plt.plot([i, j], [self.phases_coeffs[i], self.q[j]], color='gray')
            plt.savefig(self.file_analyse_dir_phases + '/' + self.file + '_peak_num_' + str(
                len(self.q_normalized_ratio) + 1) + '.pdf')
            self.reduction()


    def gathering(self):
        softmin = nn.Softmin(dim=0)
        print(self.sorted_indices_I_start)
        # self.data['phase'] = self.class_names[np.argmin(self.alignement_dict[len(self.q)])]
        self.data['phase'] = self.class_names[np.argmin(self.alignement_dict[len(self.q)])]
        self.data['distribution'] = softmin(torch.tensor(self.alignement_dict[len(self.q)], dtype=torch.float32)).tolist()
        self.data['peaks_without_suspicious'] = self.sorted_indices_I_start[self.suspicious_peaks:].tolist()
        return self.data

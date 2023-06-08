import csv

import numpy as np
import pandas as pd

from settings import *
import os

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter, find_peaks, peak_widths
from scipy.ndimage import gaussian_filter1d, gaussian_filter


def background_exponent(x, a, b):
    return b * pd.np.exp(x * a)


def background_hyberbole(x, a, b):
    return b * x ** (-a)


def gauss(x, c, b):
    return c * np.exp(-(x - 0.04) ** 2 / b)


def parabole(x, c, b):
    return c - (x - 0.04) ** 2 / (b ** 2)

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

    # def





class Peaks():
    def __init__(self, filename, DATA_DIR, current_session):

        self.peak_empty = False
        self.peak_plots = {}
        self.peaks_boundaries = np.array([])
        self.file = filename
        self.data_dir = DATA_DIR

        self.file_analyse_dir = current_session + self.file
        self.file_analyse_dir_peaks = current_session + self.file + '/peaks'

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)
        if not os.path.exists(self.file_analyse_dir_peaks):
            os.mkdir(self.file_analyse_dir_peaks)

        data = pd.read_csv(self.data_dir + self.file + EXTENSION, sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.median(self.dI)

        # self.peaks_plots = {}
        self.peaks_plots = np.array([])
        self.I_background_filtered = []
        self.popt = []
        self.pcov = []
        self.max_I = np.max(self.I)
        self.model = []
        self.difference = []
        self.peaks = []
        self.difference_start = []
        self.peaks_data = None
        self.peak_widths = np.array([])
        self.peak_previous = np.array([])
        self.zeros = np.zeros(len(self.q))
        self.peaks_analysed = np.array([])
        self.peaks_analysed_q = np.array([])
        self.peaks_analysed_I = np.array([])
        self.peaks_analysed_b = np.array([])
        self.peak_number = 0
        self.peaks_analysed_dict = {}
        self.total_fit = []
        self.peaks_detected = np.array([])
        self.start_loss = 0
        self.final_loss = 0
        self.passed = 0

        self.popt_background = []

    def background_reduction(self):

        i = np.argmax(self.q > START)
        self.q, self.I, self.dI = self.q[i:], self.I[i:], self.dI[i:]

        self.zeros = np.zeros(len(self.q))
        self.total_fit = self.zeros
        self.peaks_plots = np.zeros((20, len(self.q)))

        popt, pcov = curve_fit(
            f=background_hyberbole,
            xdata=self.q,
            ydata=self.I,
            p0=(3, 2),
            sigma=self.dI
        )

        self.popt_background = popt
        self.model = background_hyberbole(self.q, self.popt_background[0], self.popt_background[1])
        self.I_background_filtered = self.I - BACKGROUND_COEF * self.model

        # self.difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)
        # self.start_difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)

    def filtering(self):
        self.difference = gaussian_filter(self.I_background_filtered,
                                          sigma=SIGMA_FILTER,
                                          truncate=TRUNCATE,
                                          cval=0)
        self.difference_start = gaussian_filter(self.I_background_filtered,
                                                sigma=SIGMA_FILTER,
                                                truncate=TRUNCATE,
                                                cval=0)
        self.start_loss = np.mean((self.difference_start - self.total_fit) ** 2)

    def background_plot(self):
        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data_without_background')
        plt.plot(self.q, self.model, label='background')
        plt.plot(self.q, BACKGROUND_COEF * self.model, label='moderated_background')
        plt.plot(self.q, self.I, linewidth=0.5, c='b', label='raw_data')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/00_background_raw_' + self.file + '.pdf')

        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/01_background_filtered_' + self.file + '.pdf')

    def peak_searching(self, height=0, distance=5, prominence=0.1):
        self.peaks, self.peaks_data = find_peaks(self.difference,
                                                 height=height,
                                                 distance=distance,
                                                 prominence=prominence)
        # if self.peaks.size == 0:

    def peak_verifying(self):
        if self.peak_previous in self.peaks:
            self.peaks = np.delete(self.peaks, *np.where(self.peaks == self.peak_previous))
        self.peak_widths = peak_widths(self.difference, self.peaks, rel_height=0.5)

    def peak_fitting_gauss(self, i, width_factor=1):
        if np.size(self.peaks) != 0:
            period1 = self.peaks[i] - int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            period2 = self.peaks[i] + int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            gauss = lambda x, c, b: c * np.exp(-(x - self.q[self.peaks[i]]) ** 2 / (b ** 2))

            if period1 != period2:
                popt, pcov = curve_fit(
                    f=gauss,
                    xdata=self.q[period1:period2],
                    ydata=self.difference[period1:period2],
                    bounds=(self.delta_q ** 4, [2 * 2 * self.max_I, 1, ]),
                    sigma=self.dI[period1:period2]
                )

                perr = np.sqrt(np.diag(pcov))

                return gauss(self.q, popt[0], popt[1]), \
                    period1, period2, i, \
                    self.q[self.peaks[i]], \
                    gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1], self.peaks[i], perr

    def peak_fitting_substraction_gauss(self, i):
        self.peak_empty = False

        factor = 1
        peak = self.peak_fitting_gauss(i)

        if peak is None:
            self.peak_empty = True
            print('peak error empty')
            return 0


        # while peak[9][1] / peak[7] > 0.2:
        #     factor *= 0.9
        #     peak = self.peak_fitting_gauss(i, width_factor=factor)
        #     if peak is None:
        #         self.peak_empty = True
        #         return

        self.peak_plots[self.peak_number] = peak[0]


        print('peak', self.peak_number)
        print(self.file)
        print('errors%', peak[9][0] / peak[6], peak[9][1] / peak[7])




        # more efficient O(1) – previsioned array
        self.peak_previous = np.append(self.peak_previous, self.peaks[i])
        self.peaks_analysed = np.append(self.peaks_analysed,
                                        (peak[4],
                                         peak[5]))
        self.peaks_analysed_q = np.append(self.peaks_analysed_q,
                                          peak[4])
        self.peaks_analysed_I = np.append(self.peaks_analysed_I,
                                          peak[5])
        self.peaks_analysed_b = np.append(self.peaks_analysed_b,
                                          peak[7])

        self.peaks_analysed_dict[peak[4]] = peak[5]
        self.peaks_detected = np.append(self.peaks_detected, peak[8])

        self.total_fit += peak[0]
        self.difference -= peak[0]
        self.filtering_negative()
        self.stage_plot()
        self.peak_number += 1
        # self.peaks_boundaries = np.append(self.peaks_boundaries, (peak[0], peak[1]))

    def filtering_negative(self):
        for x in range(len(self.difference) - 1):
            if self.difference[x] < 0:
                self.difference[x] = 0

    def stage_plot(self):
        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.difference, 'x', label='filtered_data')
        plt.plot(self.q[self.peaks], self.difference_start[self.peaks], "x", label='all_peaks_detected')
        # if self.peak_fitting_gauss(i) is not None:
        #     plt.plot(self.q, self.peak_fitting_gauss(i)[0], linewidth=2.5, label='current_peak')
        #     plt.plot(self.q[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]],
        #              self.difference[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]], 'o',
        #              label='zone_curr_peak')

        plt.plot(self.q, self.peak_plots[self.peak_number], 'x', linewidth=2.5, label='current_peak')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.plot(self.q, self.total_fit, linewidth=2.5, label='total')
        plt.legend()
        plt.savefig(self.file_analyse_dir_peaks + '/' + self.file + '_peak:' + str(self.peak_number) + '.pdf')

    def result_plot(self):
        plt.clf()
        self.peaks_detected = self.peaks_detected.astype(int)

        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data_without_back')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data_without_back')
        # plt.plot(self.q, self.difference, label='filtered_data')
        plt.plot(self.q, self.zeros, label='zero_level')
        # plt.plot(self.q[self.peaks_detected], self.I_background_filtered[self.peaks_detected], 'x',
        #          label='peaks_on_raw_without_back')
        # plt.plot(self.q[self.peaks_detected], self.difference_start[self.peaks_detected], 'x',
        #          label='peaks_on_filtered_without_back')
        for x in range(self.peak_number):
            plt.plot(self.q, self.peak_plots[x])
        plt.plot(self.q, self.total_fit, linewidth=2, label='total')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/10_result_' + self.file + '.pdf')

        plt.clf()
        plt.plot(self.q, self.I, label='raw_data')
        plt.plot(self.q[self.peaks_detected], self.I[self.peaks_detected], 'x', label='peaks_on_raw')
        plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/11_result_raw_' + self.file + '.pdf')

        # plt.clf()
        # plt.plot(self.q, self.I, label='raw_data')
        # plt.plot(self.q[self.peaks_detected], self.I[self.peaks_detected], 'x', label='peaks_on_raw')
        # plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        # plt.legend()
        # plt.savefig(self.file_analyse_dir + '/11_result_raw_' + self.file + '.pdf')

    def get_difference_filtered(self):
        data_zipped = np.array(list(zip(self.q, self.difference, self.dI)))
        with open('data_break_peak:' + str(self.peak_number) + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            for row in data_zipped:
                writer.writerow(row)

    def peak_processing(self, number_peak=INFINITY, get=False):
        while len(self.peaks) > -1 and number_peak > 0:
            self.peak_searching(height=0, prominence=PROMINENCE)
            if len(self.peaks) == 0:
                break
            self.peak_verifying()
            if len(self.peaks) == 0:
                break
            number_peak -= 1
            self.peak_fitting_substraction_gauss(0)
            print('peak_number', self.peak_number)
        # self.stage_plot()
        if get:
            self.get_difference_filtered()

    def gathering(self):
        # print('Covariance raw', np.cov(self.difference_start, self.total_fit)[0][1])
        # print('Covariance filtered', np.cov(self.I_backfiltered, self.total_fit)[0][1])
        self.final_loss = np.mean((self.difference_start - self.total_fit) ** 2)
        # print('Covariance raw', np.mean((self.I_backfiltered-self.total_fit)**2))
        # print('Loss raw', self.start_loss)
        # print('Loss filtered', self.final_loss)

        sorted_indices_q = np.argsort(self.peaks_analysed_q)

        I = self.peaks_analysed_I[sorted_indices_q]
        q = self.peaks_analysed_q[sorted_indices_q]
        I_raw = self.I[self.peaks_detected][sorted_indices_q]
        dI = self.dI[self.peaks_detected][sorted_indices_q]
        peaks_detected = self.peaks_detected[sorted_indices_q]

        return {
            'peak_number': self.peak_number,
            'q': q.tolist(),
            'I': I.tolist(),
            'dI': dI.tolist(),
            'I_raw': I_raw.tolist(),
            'peaks': peaks_detected.tolist(),
            'start_loss': self.start_loss,
            'final_loss': self.final_loss,
            'loss_ratio': self.final_loss / self.start_loss}

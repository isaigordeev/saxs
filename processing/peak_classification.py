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


class Peaks():
    def __init__(self, filename, DATA_DIR, current_session):

        self.file = filename
        self.data_dir = DATA_DIR

        self.file_analyse_dir = current_session + self.file

        if not os.path.exists(self.file_analyse_dir):
            os.mkdir(self.file_analyse_dir)

        data = pd.read_csv(self.data_dir + self.file + EXTENSION, sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.median(self.dI)

        self.peaks_plots = []
        self.I_background_filtered = []
        self.popt = []
        self.pcov = []
        self.max_I = np.max(self.I)
        self.model = []
        self.difference = []
        self.peaks = []
        self.difference_start = []
        self.peaks_data = None
        self.peak_widths = []
        self.peak_previous = []
        self.zeros = np.zeros(len(self.q))
        self.peaks_analysed = []
        self.peaks_analysed_q = []
        self.peaks_analysed_I = []
        self.peaks_analysed_b = []
        self.peak_number = 0
        self.peaks_analysed_dict = {}
        self.total_fit = []
        self.peaks_detected = []
        self.start_loss = 0
        self.final_loss = 0

        self.popt_background = []

    def background_reduction(self):

        # do it better faster stronger
        i = 0
        for x in self.q:
            i += 1
            if x > START:
                break


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
        # self.difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)
        # self.start_difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)

    def filtering(self):
        self.I_background_filtered = self.I - BACKGROUND_COEF * self.model
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
        plt.plot(self.q, self.model, label = 'background')
        plt.plot(self.q, BACKGROUND_COEF*self.model, label = 'moderated_background')
        plt.plot(self.q, self.I, linewidth=0.5, c='b', label = 'raw_data')
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

    def peak_verifying(self):
        if self.peak_previous in self.peaks:
            self.peaks = np.delete(self.peaks, *np.where(self.peaks == self.peak_previous))
        self.peak_widths = peak_widths(self.difference, self.peaks, rel_height=0.5)

    def peak_fitting_gauss(self, i):
        if np.size(self.peaks) != 0:
            period1 = self.peaks[i] - int(SIGMA_FITTING * self.peak_widths[0][i])
            period2 = self.peaks[i] + int(SIGMA_FITTING * self.peak_widths[0][i])

            gauss = lambda x, c, b: c * np.exp(-(x - self.q[self.peaks[i]]) ** 2 / (b ** 2))

            popt, pcov = curve_fit(
                f=gauss,
                xdata=self.q[period1:period2],
                ydata=self.difference[period1:period2],
                bounds=(self.delta_q ** 4, [2 * 2 * self.max_I, 1, ]),
                sigma=self.dI[period1:period2]
            )
            return gauss(self.q, popt[0], popt[1]), \
                period1, period2, i, \
                self.q[self.peaks[i]], \
                gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1], self.peaks[i]

    def peak_fitting_parabole(self, i):
        if np.size(self.peaks) != 0:
            # width = self.peak_widths[0][i]
            # treshold = width
            width = 30
            deviation_optimal = INFINITY
            width_optimal = width
            parabole = lambda x, c, b: c - (x - self.q[self.peaks[i]]) ** 2 / (b ** 2)
            gauss = lambda x, c, b: c * np.exp(-(x - self.q[self.peaks[i]]) ** 2 / (b ** 2))

            for x in range(width, 1, -1):
                popt, pcov = curve_fit(
                    f=gauss,
                    xdata=self.q[self.peaks[i] - x:self.peaks[i] + x],
                    ydata=self.difference[self.peaks[i] - x:self.peaks[i] + x],
                    # p0 = ( 4, 0.02),
                    bounds=(delta_q ** 4, [2 * 2 * self.max_I, 1, ]),
                    sigma=dI[self.peaks[i] - x:self.peaks[i] + x]
                )

            return gauss(self.q, popt[0], popt[1]), \
                x, i, \
                self.q[self.peaks[i]], \
                gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1]

    def peak_fitting_substraction_gauss(self, i):
        peak = self.peak_fitting_gauss(i)

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
        self.peaks_plots[self.peak_number] = peak[0]
        self.peaks_detected = np.append(self.peaks_detected, peak[8])

        self.peak_number += 1
        self.total_fit += peak[0]
        self.difference -= peak[0]

    def filtering_negative(self):
        for x in range(len(self.difference) - 1):
            if self.difference[x] < 0:
                self.difference[x] = 0

    def stage_plot(self, i=0):
        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.difference, label='filtered_data')
        plt.plot(self.q[self.peaks], self.difference[self.peaks], "x", label='all_peaks_detected')
        if self.peak_fitting_gauss(i) is not None:
            plt.plot(self.q, self.peak_fitting_gauss(i)[0], linewidth=2.5, label='current_peak')
            plt.plot(self.q[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]],
                     self.difference[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]], 'o',
                     label='zone_curr_peak')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.plot(self.q, self.total_fit, linewidth=2.5, label='total')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/' + self.file + '_peak:' + str(self.peak_number) + '.pdf')

        # plt.show()

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
        plt.plot(self.q, self.total_fit, linewidth=2, label='total')
        for x in self.peaks_plots:
            if len(x) > 1:
                plt.plot(self.q, x)
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/10_result_' + self.file + '.pdf')

        plt.clf()
        plt.plot(self.q, self.I, label='raw_data')
        plt.plot(self.q[self.peaks_detected], self.I[self.peaks_detected], 'x', label='peaks_on_raw')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/11_result_raw_' + self.file + '.pdf')

    def peak_processing(self, number_peak=INFINITY):
        while len(self.peaks) > -1 and number_peak > 0:
            self.peak_searching(height=0, prominence=PROMINENCE)
            self.peak_verifying()
            if len(self.peaks) == 0:
                break
            if self.peak_fitting_gauss(0) is None:
                continue
            else:
                number_peak -= 1
                # self.peak_fitting_parabole(0)
                self.stage_plot(0)
                self.peak_fitting_substraction_gauss(0)
                self.filtering_negative()
        self.stage_plot(0)

    def gathering(self):
        # print('Covariance raw', np.cov(self.difference_start, self.total_fit)[0][1])
        # print('Covariance filtered', np.cov(self.I_backfiltered, self.total_fit)[0][1])
        self.final_loss = np.mean((self.difference_start - self.total_fit) ** 2)
        # print('Covariance raw', np.mean((self.I_backfiltered-self.total_fit)**2))
        print('Covariance raw', self.start_loss)
        print('Covariance filtered', self.final_loss)
        return {
                    'peak_number':self.peak_number,
                    'q':self.peaks_analysed_q.tolist(),
                    'I':self.peaks_analysed_I.tolist(),
                    'dI':self.dI[self.peaks_detected].tolist(),
                    'I_raw':self.I[self.peaks_detected].tolist(),
                    'peaks':self.peaks_detected.tolist(),
                    'start_loss': self.start_loss,
                    'final_loss': self.final_loss,
                    'loss_ratio': self.final_loss / self.start_loss * 100}

    def fast_Fourier(self):
        Y = np.convolve(self.difference, self.difference)
        # Y = np.fft.fft(self.difference)
        # Y = np.fft.fft(Y)
        # plt.plot(self.q , np.abs(Y).real**2+np.abs(Y).imag**2)
        plt.plot(self.q, Y[len(self.q) // 2:len(Y) - len(self.q) // 2 + 1])
        # self.difference = Y
        plt.xlabel("Frequency (k)")
        plt.ylabel("Amplitude")
        plt.title("FFT of sigma * exp(-sigma^2 * x^2) * sin(2 * pi * x * mu)")
        plt.show()

import numpy as np

from data import *

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
    def __init__(self, filename, data_directory):

        # data = pd.read_csv(data_directory + filename + extension, sep=',')
        filename_directory = analyse_directory + filename

        if not os.path.exists(filename_directory):
            os.mkdir(filename_directory)

        data = pd.read_csv(data_directory + filename, sep=',')
        data = data.apply(pd.to_numeric, errors='coerce')
        data = data.dropna()

        self.q = np.array(data.iloc[:, 0])
        self.I = np.array(data.iloc[:, 1])
        self.dI = np.array(data.iloc[:, 2])

        self.delta_q = self.q[len(self.q) - 1] / len(self.q)
        self.max_dI = np.median(self.dI)

        self.peaks_plots = []
        print(self.peaks_plots)
        self.I_backfiltered = []
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
        self.start_loss = 0
        self.final_loss = 0

    def background_reduction(self):

        # do it better
        i = 0
        for x in self.q:
            i += 1
            if x > start:
                break

        self.q, self.I, self.dI = self.q[i:], self.I[i:], self.dI[i:]
        self.total_fit = np.zeros(len(self.q))
        self.peaks_plots = np.zeros((20,len(self.q)))

        popt, pcov = curve_fit(
            f=background_hyberbole,
            xdata=self.q,
            ydata=self.I,
            p0=(3, 2),
            sigma=self.dI
        )

        self.model = background_hyberbole(self.q, popt[0], popt[1])
        # self.difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)
        # self.start_difference = savgol_filter(I - background_coef * self.model, 15, 4, deriv=0)

    def filtering(self):
        self.I_backfiltered = self.I - background_coef * self.model
        self.difference = gaussian_filter(self.I_backfiltered,
                                          sigma=sigma_filter,
                                          truncate=truncate,
                                          cval=0)
        self.difference_start = gaussian_filter(self.I_backfiltered,
                                                sigma=sigma_filter,
                                                truncate=truncate,
                                                cval=0)
        self.start_loss = np.mean((self.difference_start - self.total_fit) ** 2)

    def plot_background(self):
        plt.plot(
            # self.q, self.I,
            # self.q, self.model,
            # self.q, self.difference,
            # self.q, self.difference,
            self.q, self.zeros,
            # q, savgol_filter(I, 20 , 3, deriv=0),
            # q, np.gradient(savgol_filter(I, 20, 3, deriv=0)),
            linewidth=1
        )
        plt.show()

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
            period1 = self.peaks[i] - int(sigma_fitting * self.peak_widths[0][i])
            period2 = self.peaks[i] + int(sigma_fitting * self.peak_widths[0][i])

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
                gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1]

    def peak_fitting_parabole(self, i):
        if np.size(self.peaks) != 0:
            # width = self.peak_widths[0][i]
            # treshold = width
            width = 30
            deviation_optimal = infinity
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
        self.peak_previous = np.append(self.peak_previous, self.peaks[i])
        self.peaks_analysed = np.append(self.peaks_analysed,
                                        (self.peak_fitting_gauss(i)[4],
                                         self.peak_fitting_gauss(i)[5]))
        self.peaks_analysed_q = np.append(self.peaks_analysed_q,
                                          self.peak_fitting_gauss(i)[4])
        self.peaks_analysed_I = np.append(self.peaks_analysed_I,
                                          self.peak_fitting_gauss(i)[5])
        self.peaks_analysed_b = np.append(self.peaks_analysed_b,
                                          self.peak_fitting_gauss(i)[7])
        self.peaks_analysed_dict[self.peak_fitting_gauss(i)[4]] = self.peak_fitting_gauss(i)[4]
        self.peaks_plots[self.peak_number] = self.peak_fitting_gauss(i)[0]

        self.peak_number += 1
        self.total_fit += self.peak_fitting_gauss(i)[0]
        self.difference -= self.peak_fitting_gauss(i)[0]

    def filtering_negative(self):
        for x in range(len(self.difference) - 1):
            if self.difference[x] < 0:
                self.difference[x] = 0

    def stage_plot(self, i=0):
        plt.clf()
        plt.plot(self.q, self.I - background_coef * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.difference, label='filtered_data')
        plt.plot(self.q[self.peaks], self.difference[self.peaks], "x", label='all_peaks_detected')
        if self.peak_fitting_gauss(i) is not None:
            plt.plot(self.q, self.peak_fitting_gauss(i)[0], linewidth=2.5, label='current_peak')
            plt.plot(self.q[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]],
                     self.difference[self.peak_fitting_gauss(i)[1]:self.peak_fitting_gauss(i)[2]], 'o',
                     label='zone_curr_peak')
        plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        plt.plot(self.q, self.total_fit, linewidth=2.5, label='total')
        plt.legend()

        plt.savefig(filename_directory + '/' + filename + str(self.peak_number) + '.pdf')

        # plt.show()

    def result_plot(self):
        plt.clf()
        plt.plot(self.q, self.I - background_coef * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.difference, label='filtered_data')
        plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        plt.plot(self.q, self.total_fit, linewidth=2.5, label='total')
        for x in self.peaks_plots:
            if len(x) > 1:
                plt.plot(self.q, x)
        plt.legend()

        plt.savefig(filename_directory + '/result_' + filename + str(self.peak_number) + '.pdf')

    def phase_classification(self, number_peak=infinity):
        while len(self.peaks) > -1 and number_peak > 0:
            self.peak_searching(height=0, prominence=prominence)
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

    def loss(self):
        # print('Covariance raw', np.cov(self.difference_start, self.total_fit)[0][1])
        # print('Covariance filtered', np.cov(self.I_backfiltered, self.total_fit)[0][1])
        self.final_loss = np.mean((self.difference_start - self.total_fit) ** 2)
        # print('Covariance raw', np.mean((self.I_backfiltered-self.total_fit)**2))
        print('Covariance raw', self.start_loss)
        print('Covariance filtered', self.final_loss)
        return self.final_loss / self.start_loss * 100

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

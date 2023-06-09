import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit, minimize
from scipy.signal import find_peaks, peak_widths

from processing.functions import background_hyberbole, gaussian_sum, moving_average
from processing.peak_classification import PeakClassificator
from settings import INFINITY, PROMINENCE, BACKGROUND_COEF, SIGMA_FITTING, SIGMA_FILTER, TRUNCATE, START


class Peaks(PeakClassificator):
    def __init__(self, filename, DATA_DIR, current_session):

        super().__init__(filename, DATA_DIR=DATA_DIR, current_session=current_session)

        # self.peaks_plots = {}
        self.params = np.array([])
        self.widths = np.array([])
        self.peak_plots = {}
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

        self.gauss = True
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
        if self.gauss:
            self.difference = gaussian_filter(self.I_background_filtered,
                                              sigma=SIGMA_FILTER,
                                              truncate=TRUNCATE,
                                              cval=0)
            self.difference_start = gaussian_filter(self.I_background_filtered,
                                                    sigma=SIGMA_FILTER,
                                                    truncate=TRUNCATE,
                                                    cval=0)
            self.start_loss = np.mean((self.difference_start - self.total_fit) ** 2)

    def custom_filtering(self):
        y = self.I_background_filtered
        window_size = 5
        smoothed_y = moving_average(y, window_size)

        # plt.plot(self.q, y, label='Original')
        plt.legend()
        # plt.show()


        sigma_values = np.linspace(0.5, 5.0, 10)

        best_sigma = None
        best_metric = np.inf

        # Perform grid search
        for sigma in sigma_values:
            smoothed_difference = gaussian_filter(self.I_background_filtered,
                                                  sigma=sigma,
                                                  truncate=4.0)

            metric = np.mean(np.square(smoothed_difference - smoothed_y))

            if metric < best_metric:
                best_metric = metric
                best_sigma = sigma

        # Output the best sigma value and the corresponding metric
        print("Best range: ", best_sigma)
        print("Best range_Metric: ", best_metric)
        plt.clf()
        self.difference_start = gaussian_filter(self.I_background_filtered,
                                                  sigma=best_sigma,
                                                  truncate=4.0)
        self.difference = gaussian_filter(self.I_background_filtered,
                                                  sigma=best_sigma,
                                                  truncate=4.0)
        plt.plot(self.q, gaussian_filter(self.I_background_filtered,
                                                  sigma=best_sigma,
                                                  truncate=4.0))
        plt.plot(self.q, self.I_background_filtered, label='gde')
        plt.plot(self.q, smoothed_y, label='Smoothed')
        plt.legend()
        plt.savefig('heap/filter ' + self.filename+'.pdf')

    
    def background_plot(self):
        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data_without_background')
        plt.plot(self.q, self.model, label='background')
        plt.plot(self.q, BACKGROUND_COEF * self.model, label='moderated_background')
        plt.plot(self.q, self.I, linewidth=0.5, c='b', label='raw_data')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/00_background_raw_' + self.filename + '.pdf')

        plt.clf()
        plt.plot(self.q, self.I - BACKGROUND_COEF * self.model, linewidth=0.5, label='raw_data')
        plt.plot(self.q, self.difference_start, label='filtered_raw_data')
        plt.plot(self.q, self.zeros, label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/01_background_filtered_' + self.filename + '.pdf')

    def peak_searching(self, height=0, distance=5, prominence=0.1):
        self.peaks, self.peaks_data = find_peaks(self.difference,
                                                 height=height,
                                                 distance=distance,
                                                 prominence=prominence)
        # if self.peaks.size == 0:
        print(self.peaks_data)

    def peak_verifying(self):
        if self.peak_previous in self.peaks:
            self.peaks = np.delete(self.peaks, *np.where(self.peaks == self.peak_previous))
        self.peak_widths = peak_widths(self.difference, self.peaks, rel_height=0.6)


    def custom_peak_fitting(self, i, width_factor=1):
        if np.size(self.peaks) != 0:
            delta = min(abs(self.peaks[i] - self.peaks_data['left_bases'][i]), abs(self.peaks[i] - self.peaks_data['right_bases'][i]))
            # period1 = self.peaks[i] - int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            # period2 = self.peaks[i] + int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            period1 = self.peaks[i] - delta
            period2 = self.peaks[i] + delta

            start_delta = delta

            gauss = lambda x, c, b: c * np.exp(-(x - self.q[self.peaks[i]]) ** 2 / (b ** 2))

            y = self.I_background_filtered
            window_size = 5
            smoothed_y = moving_average(y, window_size)

            # plt.plot(self.q, y, label='Original')
            plt.legend()
            # plt.show()

            sigma_values = np.linspace(4, start_delta, 10)

            best_sigma = None
            best_metric = np.inf



            # Perform grid search
            for delta in sigma_values:
                period1 = int(self.peaks[i] - delta)
                period2 = int(self.peaks[i] + delta)

                if period1 != period2:

                    popt, pcov = curve_fit(
                        f=gauss,
                        xdata=self.q[period1:period2],
                        ydata=self.difference[period1:period2],
                        bounds=(self.delta_q ** 4, [2 * 2 * self.max_I, 1, ]),
                        sigma=self.dI[period1:period2]
                    )

                    smoothed_difference = gauss(self.q, popt[0], popt[1])

                    metric = np.mean(np.square(smoothed_difference[period1:period2] - self.difference[period1:period2]))

                    if metric < best_metric:
                        best_metric = metric
                        best_delta = delta

            # Output the best sigma value and the corresponding metric
            print("Best Sigma: ", best_delta)
            print("Best Metric: ", best_metric)

            period1 = int(self.peaks[i] - best_delta)
            period2 = int(self.peaks[i] + best_delta)

            popt, pcov = curve_fit(
                f=gauss,
                xdata=self.q[period1:period2],
                ydata=self.difference[period1:period2],
                bounds=(self.delta_q ** 4, [2 * 2 * self.max_I, 1, ]),
                sigma=self.dI[period1:period2]
            )

            perr = best_metric

            self.params = np.append(self.params, popt[0])
            self.params = np.append(self.params, self.q[self.peaks[i]])
            self.params = np.append(self.params, popt[1])

            plt.clf()
            plt.plot(self.q, gauss(self.q, popt[0], popt[1]))
            plt.plot(self.q, self.I_background_filtered)
            plt.plot(self.q[period1:period2], self.I_background_filtered[period1:period2])
            plt.savefig('heap/' + str(self.peak_number)+'.png')

            return gauss(self.q, popt[0], popt[1]), \
                period1, period2, i, \
                self.q[self.peaks[i]], \
                gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1], self.peaks[i], perr

    def peak_fitting(self, i, width_factor=1):
        if np.size(self.peaks) != 0:
            delta = min(abs(self.peaks[i] - self.peaks_data['left_bases'][i]),
                        abs(self.peaks[i] - self.peaks_data['right_bases'][i]))
            # period1 = self.peaks[i] - int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            # period2 = self.peaks[i] + int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
            period1 = self.peaks[i] - delta
            period2 = self.peaks[i] + delta

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

                self.params = np.append(self.params, popt[0])
                self.params = np.append(self.params, self.q[self.peaks[i]])
                self.params = np.append(self.params, popt[1])

                plt.clf()
                plt.plot(self.q, gauss(self.q, popt[0], popt[1]))
                plt.plot(self.q, self.I_background_filtered)
                plt.plot(self.q[period1:period2], self.I_background_filtered[period1:period2])
                plt.savefig('heap/' + str(self.peak_number) + '.png')

                return gauss(self.q, popt[0], popt[1]), \
                    period1, period2, i, \
                    self.q[self.peaks[i]], \
                    gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1], self.peaks[i], perr

    def peak_substraction(self, i):
        self.peak_empty = False

        factor = 1
        peak = self.custom_peak_fitting(i)

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
        self.widths = np.append(self.peak_widths,
                                     self.peak_widths[0][i])

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
        plt.savefig(self.file_analyse_dir_peaks + '/' + self.filename + '_peak:' + str(self.peak_number) + '.pdf')

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
        plt.savefig(self.file_analyse_dir + '/10_result_' + self.filename + '.pdf')

        plt.clf()
        plt.plot(self.q, self.I, label='raw_data')
        plt.plot(self.q[self.peaks_detected], self.I[self.peaks_detected], 'x', label='peaks_on_raw')
        plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        plt.legend()
        plt.savefig(self.file_analyse_dir + '/11_result_raw_' + self.filename + '.pdf')

        # plt.clf()
        # plt.plot(self.q, self.I, label='raw_data')
        # plt.plot(self.q[self.peaks_detected], self.I[self.peaks_detected], 'x', label='peaks_on_raw')
        # plt.plot(self.q, np.zeros(len(self.q)), label='zero_level')
        # plt.legend()
        # plt.savefig(self.file_analyse_dir + '/11_result_raw_' + self.file + '.pdf')

    
    def peak_processing(self, number_peak=INFINITY, get=False):
        while len(self.peaks) > -1 and number_peak > 0:
            self.peak_searching(height=0, prominence=PROMINENCE)
            if len(self.peaks) == 0:
                break
            self.peak_verifying()
            if len(self.peaks) == 0:
                break
            number_peak -= 1
            self.peak_substraction(0)
            # print('peak_number', self.peak_number)

    def sum_total_fit(self):
        if(len(self.params) != 0):
            def loss_function(params):
                y_pred = gaussian_sum(self.q, *params)
                return np.sum((y_pred - self.I_background_filtered) ** 2)

            result = minimize(loss_function, self.params, method='BFGS')
            fitted_params = result.x
            y_fit = gaussian_sum(self.q, *fitted_params)

            plt.clf()
            plt.plot(self.q, self.I_background_filtered, 'g--', label='True Gaussian Sum')
            plt.plot(self.q, y_fit, 'r-', label='Fitted Gaussian Sum')
            plt.legend()
            plt.xlabel('x')
            plt.ylabel('y')
            plt.savefig('heap/fittotal'+self.filename+ '.png')
            # plt.show()

        else:
            plt.plot(self.q, self.I_background_filtered, 'g--', label='True Gaussian Sum')
            plt.legend()
            plt.xlabel('x')
            plt.ylabel('y')
            plt.savefig('heap/fittotal'+self.filename+ '.png')




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
        print(self.params)

        return {
            'peak_number': self.peak_number,
            'q': q.tolist(),
            'I': I.tolist(),
            'dI': dI.tolist(),
            'I_raw': I_raw.tolist(),
            'peaks': peaks_detected.tolist(),
            # 'width': widths.tolist(),
            'start_loss': self.start_loss,
            'final_loss': self.final_loss,
            'loss_ratio': self.final_loss / self.start_loss}


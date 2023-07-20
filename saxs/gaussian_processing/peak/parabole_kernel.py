import numpy as np
from matplotlib import pyplot as plt

from prominence_kernel import ProminenceKernel


class ParabolePeakKernel(ProminenceKernel):
    def __init__(self, data_dir,
                 is_preprocessing=True,
                 is_background_reduction=True,
                 is_filtering=True,
                 ):
        super().__init__(data_dir,
                         is_preprocessing,
                         is_background_reduction,
                         is_filtering,
                         )

    def negative_reduction(self):
        self.difference = np.maximum(self.current_I_state, 0)

    def custom_peak_fitting_with_parabole(self, i):
        if len(self.peaks) > i:
            if np.size(self.peaks) != 0:
                left_base = abs(self.peaks[i] - self.peaks_data['left_bases'][i])
                right_base = abs(self.peaks[i] - self.peaks_data['right_bases'][i])
                delta = min(left_base, right_base) / 2
                start_delta = delta

                delta = 3
                print(left_base, right_base, 'bases')
                # period1 = self.peaks[i] - int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])
                # period2 = self.peaks[i] + int(width_factor * SIGMA_FITTING * self.peak_widths[0][i])

                y = self.I_cut_background_reduced
                window_size = 5
                smoothed_y = moving_average(y, window_size)

                sigma_values = np.linspace(3, 20, 5)  # NOTE optimine

                best_metric = np.inf

                period1 = int(self.peaks[i] - delta)
                period2 = int(self.peaks[i] + delta)

                print(period1, period2, 'perods')

                current_peak_parabole = lambda x, sigma, ampl: parabole(x, self.q[self.peaks[i]], sigma, ampl)

                popt, pcov = curve_fit(
                    f=current_peak_parabole,
                    xdata=self.q[period1:period2],
                    ydata=self.difference_start[period1:period2],
                    bounds=([self.delta_q ** 2, 1], [0.05, 4 * self.max_I]),
                    sigma=self.dI[period1:period2]
                )

                print(popt)
                print(pcov)

                period2 = int(self.peaks[i] + start_delta)
                period1 = int(self.peaks[i] - start_delta)

                current_parabole = current_peak_parabole(self.q, popt[0], popt[1])[period1:period2]
                plt.clf()
                plt.plot(self.current_q_state[period1:period2], current_parabole)
                plt.plot(self.current_q_state[period1:period2], self.I_cut_background_reduced[period1:period2], 'x')
                plt.title(f'{popt},{np.sqrt(np.diag(pcov))}')
                print({popt[0] / self.delta_q})
                plt.savefig(('heap/parabole_' + str(self.peak_number) + '.png'))

                # return gauss(self.q, popt[0], popt[1]), \
                #     period1, period2, i, \
                #     self.q[self.peaks[i]], \
                #     gauss(self.q, popt[0], popt[1])[self.peaks[i]], popt[0], popt[1], self.peaks[i], perr



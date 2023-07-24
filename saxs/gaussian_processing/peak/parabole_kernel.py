import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

from .prominence_kernel import ProminenceKernel
from saxs.gaussian_processing.functions import parabole


class ParabolePeakKernel(ProminenceKernel):
    def __init__(self, data_dir, file_analysis_dir,
                 is_preprocessing=True,
                 is_background_reduction=True,
                 is_filtering=True,
                 is_peak_processing=True
                 ):

        super().__init__(data_dir, file_analysis_dir,
                         is_preprocessing,
                         is_background_reduction,
                         is_filtering,
                         is_peak_processing
                         )

        self.parabole_number = 0
        self.parabole_popt_for_gauss = {}

    def negative_reduction(self):
        self.difference = np.maximum(self.current_I_state, 0)

    def custom_peak_fitting_with_parabole(self, i):
        if len(self.peaks) > i:
            if np.size(self.peaks) != 0:
                left_base = abs(self.peaks[i] - self.props['left_bases'][i])
                right_base = abs(self.peaks[i] - self.props['right_bases'][i])

                delta = min(left_base, right_base) / 2

                start_delta = delta

                period1 = int(self.peaks[i] - delta)
                period2 = int(self.peaks[i] + delta)

                print(period1, period2, 'perods')

                current_peak_parabole = lambda x, sigma, ampl: parabole(x, self.current_q_state[self.peaks[i]], sigma, ampl)

                popt, pcov = curve_fit(
                    f=current_peak_parabole,
                    xdata=self.current_q_state[period1:period2],
                    ydata=self.current_I_state[period1:period2],
                    bounds=([self.delta_q ** 2, 1], [0.05, 4 * self.max_I]),
                    sigma=self.dI[period1:period2]
                )


                period2 = int(self.peaks[i] + start_delta)
                period1 = int(self.peaks[i] - start_delta)

                current_parabole = current_peak_parabole(self.current_q_state, popt[0], popt[1])
                plt.clf()
                plt.plot(self.current_q_state, self.current_I_state)
                # plt.plot(self.current_q_state[period1//2:period2*2], current_parabole[period1//2:period2*2])
                plt.plot(self.current_q_state[period1:period2], self.current_I_state[period1:period2])
                plt.plot(self.current_q_state[period1:period2], current_parabole[period1:period2], 'red')

                plt.title(f'{popt},{np.sqrt(np.diag(pcov))}')
                plt.savefig('{}parabole_{}.png'.format(self.file_analysis_dir_peaks, self.parabole_number))

                self.parabole_number += 1
                self.parabole_popt_for_gauss[self.peaks[i]] = popt




    def search_peaks(self, height=1, prominence=0.3):
        super().search_peaks(height, prominence)

        self.custom_peak_fitting_with_parabole(0)
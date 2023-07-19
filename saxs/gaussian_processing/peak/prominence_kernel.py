import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks, medfilt

from saxs.gaussian_processing.functions import moving_average
from saxs.gaussian_processing.peak.abstract_kernel import AbstractPeakKernel
from saxs.gaussian_processing.peak.default_kernel import DefaultPeakKernel
from saxs.gaussian_processing.settings_processing import START


class ProminenceKernel(DefaultPeakKernel):
    str_type = 'prominence_kernel'
    short_str_type = 'prom_kern'

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

        self.peaks = None

    def preprocessing(self):
        self.default_preprocessing()
        self.detecting_relevant_noisy()
        self.prefiltering_decomposition()

        # print(len(self.current_q_state))
        # print(len(self.current_I_state))
        # print(len(self.dI))

    def detecting_relevant_noisy(self):
        self.peaks, props = find_peaks(self.current_I_state, height=1, prominence=1)
        print(props["left_bases"])
        print(props["right_bases"])
        print(self.peaks)
        print(props["right_bases"][0])
        self.noisy_relevant_cut_point = props["right_bases"][0]

        # plt.plot(self.current_q_state[self.peaks], self.current_I_state[self.peaks], 'rx', label='peaks')
        # plt.plot(self.current_q_state[props["left_bases"]], self.current_I_state[props["left_bases"]], 'gx', label='peaks')
        # plt.plot(self.current_q_state[props["right_bases"]], self.current_I_state[props["right_bases"]], 'bx', label='peaks')
        # plt.show()
        # plt.plot(self.q, self.I_background_reduced)
        # plt.plot(self.q[_["right_bases"][0]], self.I_background_reduced[_["left_bases"][0]], 'ro')

    def prefiltering_decomposition(self):
        # noisy_part = np.ones(noisy_indice)
        self.detecting_relevant_noisy()

        noisy_part = moving_average(self.current_I_state[:self.noisy_relevant_cut_point], 10)

        # noiseless_part = medfilt(self.I_background_reduced[noisy_indice:], 3)
        noiseless_part = self.current_I_state[self.noisy_relevant_cut_point:]

        self.current_I_state = medfilt(np.concatenate((noisy_part, noiseless_part)), 3)

        # self.I_filt = medfilt(good_smoothed_without_loss, 3)
        # _, __ = find_peaks(self.I_denoised, height=1, prominence=1)
        # plt.plot(self.q, self.I_denoised)
        # plt.plot(self.q, self.I_background_reduced)
        # plt.plot(self.q[_], self.I_background_reduced[_], 'ro')
        # plt.show()
        # plotting
        # plt.plot(self.q[noisy_indice:], medfilt(self.I_background_reduced[noisy_indice:], 3))
        # plt.plot(self.q[:noisy_indice], noisy_part)
        # plt.plot(self.q[noisy_indice:], noiseless_part)
        # plt.show()

    def search_peaks(self):
        self.peaks, props = find_peaks(self.current_I_state, height=1, prominence=0.3)
        # print(self.current_q_state[self.peaks])
        # self.current_state_plot()
        # self.peaks_plots()

    def gathering(self) -> dict:
        return {
            'peak_number': len(self.peaks),
            'q': self.current_q_state[self.peaks].tolist(),
            'I': self.current_q_state[self.peaks].tolist(),
            # 'dI': dI.tolist(),
            # 'I_raw': I_raw.tolist(),
            # 'peaks': peaks_detected.tolist(),
            # 'params_amplitude': self.params.tolist()[::3],
            # 'params_mean': self.params.tolist()[1::3],
            # 'params_sigma': self.params.tolist()[2::3],
            # 'start_loss': self.start_loss,
            # 'final_loss': self.final_loss,
            # 'error': error
            # 'loss_ratio': self.final_loss / self.start_loss
        }

class SyntheticKernel(ProminenceKernel):
    def __init__(self, data_dir,
                 is_preprocessing=False,
                 is_background_reduction=False,
                 is_filtering=False,
                 ):
        super().__init__(data_dir,
                         is_preprocessing,
                         is_background_reduction,
                         is_filtering,
                         )

class RobustProminence(ProminenceKernel):
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
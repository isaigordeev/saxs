import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks

from saxs.gaussian_processing.peak.abstract_kernel import AbstractPeakKernel
from saxs.gaussian_processing.peak.default_kernel import DefaultPeakKernel
from saxs.gaussian_processing.settings_processing import START


class ProminenceKernel(DefaultPeakKernel):

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

        self.sample_processing()

    def preprocessing(self):
        self.default_preprocessing()
        self.detecting_relevant_noisy()

    def detecting_relevant_noisy(self):
        peaks, props = find_peaks(self.current_I_state, height=1, prominence=1)
        print(props["left_bases"])
        print(props["right_bases"])
        print(peaks)
        print(props["right_bases"][0])
        self.state_plot()
        plt.show()
        # plt.plot(self.q, self.I_background_reduced)
        # plt.plot(self.q[_["right_bases"][0]], self.I_background_reduced[_["left_bases"][0]], 'ro')

    def filtering0(self):
        self.I_background_reduced = np.concatenate((np.zeros(self.cut_point), self.I_cut_background_reduced))

        # y = self.I_cut_background_reduced
        y = self.I_background_reduced
        window_size = 10

        self.difference = moving_average(y, window_size)
        self.difference_start = moving_average(y, window_size)

        # self.difference = gaussian_filter(self.I_background_filtered,
        #                                   sigma=SIGMA_FILTER,
        #                                   truncate=TRUNCATE,
        #                                   cval=0)
        # self.difference_start = gaussian_filter(self.I_background_filtered,
        #                                         sigma=SIGMA_FILTER,
        #                                         truncate=TRUNCATE,
        #                                         cval=0)

        # plt.plot(self.I_cut_background_reduced)
        # plt.plot(self.I_cut)
        peaks, _ = find_peaks(self.difference, height=1, prominence=0.5)

        plt.plot(self.q, self.difference)
        plt.plot(self.q[peaks], self.difference[peaks], 'x')
        plt.show()

        self.I_background_reduced = np.concatenate((np.zeros(self.cut_point), self.I_cut_background_reduced))
        peaks, _ = find_peaks(self.I_background_reduced, height=1, prominence=1)
        print(_["left_bases"])
        print(_["right_bases"])
        print(peaks)
        plt.plot(self.q, self.I_background_reduced)
        plt.plot(self.q[_["right_bases"][0]], self.I_background_reduced[_["left_bases"][0]], 'ro')

        plt.plot(self.q[peaks], self.I_background_reduced[peaks], 'x')
        plt.show()

    def noisy_parts_detection(self):
        peaks, properties = find_peaks(self.I_background_reduced, height=1, prominence=1)
        return properties['right_bases'][0]

    def denoising(self):
        noisy_indice = self.noisy_parts_detection()

        # noisy_part = np.ones(noisy_indice)
        noisy_part = moving_average(self.I_background_reduced[:noisy_indice], 10)

        # noiseless_part = medfilt(self.I_background_reduced[noisy_indice:], 3)
        noiseless_part = self.I_background_reduced[noisy_indice:]

        self.I_denoised = medfilt(np.concatenate((noisy_part, noiseless_part)), 3)
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

    def prefiltering_(self):

        noisy_indices = self.noisy_parts_detection()
        print(noisy_indices)
        first_part = medfilt(self.I[:max(noisy_indices)], 3)
        first_part = savgol_filter(self.I[:max(noisy_indices)], 15, 4, deriv=0)

        # first_part = gaussian_filter(first_part, sigma=10)

        # first_part = gaussian_filter(self.I[:max(noisy_indices)], sigma=10)
        # first_part = medfilt(first_part, 3)
        print('FILTERING {}'.format(self.filename))

        sec_part = medfilt(self.I[max(noisy_indices):], 3)
        good_smoothed_without_loss = np.concatenate((first_part, sec_part))

        # return medfilt(good_smoothed_without_loss, 3)

        self.I_filt = medfilt(good_smoothed_without_loss, 3)





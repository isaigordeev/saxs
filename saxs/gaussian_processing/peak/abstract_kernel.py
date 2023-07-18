import numpy as np
from scipy.optimize import curve_fit

from saxs.gaussian_processing.functions import background_hyberbole
from saxs.gaussian_processing.processing_outils import read_data
import matplotlib.pyplot as plt

from saxs.gaussian_processing.settings_processing import BACKGROUND_COEF


class AbstractPeakKernel:
    __slots__ = ('I_raw',
                 'q_raw',
                 'I_cut',
                 'q_cut',
                 'dI',
                 'data_dir',
                 'current_I_state',
                 'current_q_state',
                 'is_background_reduction',
                 'is_preprocessing',
                 'is_filtering',
                 'popt_background',
                 'pcov_background',
                 'background',
                 'zero_level',
                 'total_fit',
                 'I_background_filtered',
                 'max_I',
                 'peaks',
                 'str_type',
                 'short_str_type'
                 )

    @classmethod
    def class_short_info(cls):
        return cls.short_str_type

    @classmethod
    def class_info(cls):
        return cls.str_type

    def __init__(self, data_dir,
                 is_preprocessing=True,
                 is_background_reduction=True,
                 is_filtering=True,
                 ):

        self.data_dir = data_dir
        self.q_raw, self.I_raw, self.dI = read_data(self.data_dir)

        # print(self.q_raw)

        self.max_I = None
        self.I_background_filtered = None
        self.zero_level = np.zeros(len(self.q_raw))
        self.total_fit = self.zero_level

        self.data_dir = data_dir

        self.current_I_state = self.I_raw
        self.current_q_state = self.q_raw

        self.is_preprocessing = is_preprocessing
        self.is_background_reduction = is_background_reduction
        self.is_filtering = is_filtering

        self.background = None
        self.popt_background = None
        self.pcov_background = None

        self.str_type = 'abstract_kernel'
        self.short_str_type = 'abs_kern'



    def __call__(self, *args, **kwargs):
        self.sample_processing()
        return self.gathering()

    def __str__(self):
        print(self.short_str_type)
        return ''.join(self.short_str_type)


    def current_state_plot(self):
        # plt.clf()
        plt.plot(self.current_q_state, self.current_I_state, label='current_state')

    def raw_plot(self):
        # plt.clf()
        plt.plot(self.q_raw, self.I_raw, label='very initial_state')
        plt.legend()

    def peaks_plots(self):
        plt.plot(self.current_q_state[self.peaks], self.current_I_state[self.peaks], 'rx', label='peaks')
        plt.legend()


    def extended_peaks_plots(self):
        plt.plot(self.current_q_state[self.peaks], self.current_I_state[self.peaks], 'rx', label='peaks')
        plt.legend()

    def background_plot(self):
        plt.plot(self.current_q_state, self.I_background_filtered, label='background')
        # plt.plot(self.current_q_state, self.I_raw[len(self.I_raw)-len(self.current_q_state):], label='background')
        plt.legend()


    def preprocessing(self):
        # self.I_filt = self.I_filt[i:]
        pass

    def background_reduction(self):
        pass

    def search_peaks(self, *args):
        pass


    def filtering(self):
        pass

    def gathering(self) -> dict:
        pass

    def sample_processing(self):
        if self.is_preprocessing:
            self.preprocessing()
        if self.is_background_reduction:
            self.background_reduction()
            self.background_plot()
            plt.show()
        if self.is_filtering:
            self.filtering()
















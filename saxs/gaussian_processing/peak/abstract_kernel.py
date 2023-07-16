import numpy as np
from scipy.optimize import curve_fit

from saxs.gaussian_processing.functions import background_hyberbole
from saxs.gaussian_processing.processing_outils import read_data
import matplotlib.pyplot as plt

from saxs.gaussian_processing.settings_processing import BACKGROUND_COEF


class AbstractPeakKernel:
    __slots__ = ('I_raw',
                 'q_raw',
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
                 'max_I')

    def __init__(self, data_dir,
                 is_preprocessing=True,
                 is_background_reduction=True,
                 is_filtering=True,
                 ):
        self.q_raw, self.I_raw, self.dI = read_data(self.data_dir)


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


    def state_plot(self):
        plt.clf()
        plt.plot(self.current_q_state, self.current_I_state, label='current_state')

    def raw_plot(self):
        plt.clf()
        plt.plot(self.q_raw, self.I_raw, label='very initial_state')

    def preprocessing(self):
        # self.I_filt = self.I_filt[i:]
        pass

    def background_reduction(self):
        pass

    def search_peaks(self, *args):
        pass


    def filtering(self):
        pass


    def sample_processing(self):
        if self.is_preprocessing:
            self.preprocessing()
        if self.is_background_reduction:
            self.background_reduction()
        if self.is_filtering:
            self.filtering()












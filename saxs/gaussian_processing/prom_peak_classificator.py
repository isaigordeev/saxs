import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit, minimize
from scipy.signal import find_peaks, peak_widths, medfilt, savgol_filter

from .functions import background_hyberbole, gaussian_sum, moving_average, gauss, parabole
from .abstr_peak import AbstractPeakClassificator
from .settings_processing import INFINITY, PROMINENCE, BACKGROUND_COEF, SIGMA_FITTING, SIGMA_FILTER, TRUNCATE, START, \
    WINDOWSIZE, \
    RESOLUTION_FACTOR



class ProminencePeakClassificator(AbstractPeakClassificator):
    def __init__(self, current_session, data_directory):
        super().__init__(current_session, data_directory)







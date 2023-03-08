import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit

from processing.peak_classification import background_hyberbole
from settings import BACKGROUND_COEF, START, SIGMA_FILTER, TRUNCATE




def read_data(data_dir_file, EXTENSION):
    data = pd.read_csv(data_dir_file + EXTENSION, sep=',')
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.dropna()
    q = np.array(data.iloc[:, 0])
    I = np.array(data.iloc[:, 1])
    dI = np.array(data.iloc[:, 2])
    return q, I, dI

def read_I(data_dir_file, EXTENSION):
    data = pd.read_csv(data_dir_file + EXTENSION, sep=',')
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.dropna()
    I = np.array(data.iloc[:, 0])
    return I

def background_plot(q, I):
    plt.clf()
    plt.plot(q, I, linewidth=0.5, label='raw_data')
    plt.show()
    # plt.savefig('1')


def background_reduction(q, I, dI):
    i = np.argmax(q > START)
    q, I, dI = q[i:], I[i:], dI[i:]

    zeros = np.zeros(len(q))
    total_fit = zeros
    peaks_plots = np.zeros((20, len(q)))

    popt, _ = curve_fit(
        f=background_hyberbole,
        xdata=q,
        ydata=I,
        p0=(3, 2),
        sigma=dI
    )

def fitting_parabole(q, I):
    I_max = np.max(I)
    I_i = np.argmax(I)
    delta_q = q[-1] / len(q)

    parabole = lambda x, c, b: c - (x - I_max) ** 2 / (b ** 2)
    width = 20
    for x in range(width, 1, -1):
        popt, pcov = curve_fit(
            f=parabole,
            xdata=q[I_i - x:I_i + x],
            ydata=I[I_i - x:I_i + x],
            # p0 = ( 4, 0.02),
            bounds=(delta_q ** 4, [2 * 2 * I_max, 1, ]),
            sigma=dI[I_i - x:I_i + x]
        )
        pcov

def filtering(I, model):
    I_background_filtered = I - BACKGROUND_COEF * model
    difference = gaussian_filter(I_background_filtered,
                                      sigma=SIGMA_FILTER,
                                      truncate=TRUNCATE,
                                      cval=0)
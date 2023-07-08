import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit

from saxs_processing.functions import background_hyberbole
from settings_processing import BACKGROUND_COEF, START, SIGMA_FILTER, TRUNCATE

def load_generated_data(phase):
    data = np.load(f'../saxs_generated_data/P_{phase.lower()}.npy')
    print(data.shape)
    data_3d = data[:,:,:,0]
    data_1d = []
    for i in data_3d:
        # get matrix diagonal
        data = np.sqrt(np.diag(i))
        data_1d.append(data)
    data_1d = np.array(data_1d)
    q = np.load(f'../saxs_generated_data/{phase.lower()}_q.npy')
    # load experimental data
    # exp_data = np.load(f'Experimental_data/{phase.lower()}.npy')
    exp_data = None
    return data_1d, data_3d, exp_data, q

def write_generated_data_to_csv(q, I, filename):
    csv_file = filename

    data = np.array([q,I], dtype=object)
    data = np.transpose(data)
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerows(data)

    print(f'Data written to {csv_file} successfully.')



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
    plt.plot(q, I,'bo', linewidth=0.5,  label='raw_data')
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


def filtering(I, model):
    I_background_filtered = I - BACKGROUND_COEF * model
    difference = gaussian_filter(I_background_filtered,
                                      sigma=SIGMA_FILTER,
                                      truncate=TRUNCATE,
                                      cval=0)


def calculate_absolute_difference(sequence, target):
    sequence = sequence[:len(target)]
    absolute_difference = np.sum([1/abs(x-y) for x,y in zip(sequence,target)])
    return absolute_difference

# I, _, __, q = load_generated_data('cubic')
#
# write_generated_data_to_csv(q, I[7], 'sample.csv')
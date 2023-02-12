import numpy as np
import pandas as pd

import random
from math import pi

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import csv

import pylab
from scipy.signal import savgol_filter

# data = pd.read_csv("res/075773_treated_xye.csv", sep=',')
data = pd.read_csv("res/075775_treated_xye.csv", sep=',')

data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

q = np.array(data.iloc[:, 0])
I = np.array(data.iloc[:, 1])
dI = np.array(data.iloc[:, 2])


delta_q = q[len(q)-1]/len(q)
max_dI = np.median(dI)


start = 0.02
background_coef = 0.8
sigma_filter = 3
sigma_fitting = 0.3
truncate = 3
prominence = 0.2


def filtering_start_noise(q, I, dI):
    i = 0
    for x in q:
        i += 1
        if x > start:
            break
    return q[i:], I[i:], dI[i:]



q, I, dI = filtering_start_noise(q, I, dI)
# print(len(q))

# plt.plot(I, 'x')
# plt.show()
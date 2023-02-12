from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
import random
from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("data/095221_xye.csv", sep=';')
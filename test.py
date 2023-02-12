from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
import random
from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# df = pd.read_csv("data/095221_xye.csv", sep=';')
df = pd.read_csv("data/075775_treated_xye.csv", sep=',')

df = df.dropna()
# df = df[200:]
y = df['I']
y = savgol_filter(y, 20, 3, deriv=0)

y_median = np.mean(y)

# plt.plot(y)





def background_f(x, a, c):
    return c*pd.np.exp(x*a)

def factor(x,a):
    return np.dot(a,x)

popt, pcov = curve_fit(
    f=background_f,       # model function
    xdata=df["Q"],   # x data
    ydata=df["I"],   # y data
    p0=(-10, 4),      # initial value of the parameters
    sigma=df["Di"]   # uncertainties on y
)
print(np.sqrt(np.diag(pcov)))
print(popt)

df["model"] = background_f(df["Q"], popt[0], popt[1])
df['model'] = df['model']
plt.plot(np.arange(len(y)), y, np.arange(len(y)),df['model'] )
peaks, _ = find_peaks(y, height=factor(df['model'],1.2), distance=5)
plt.plot(np.arange(len(y)), y, peaks, y[peaks],  "x")
plt.show()
import random
from math import pi

# manage data and fit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

import csv

import pylab
from scipy.signal import savgol_filter


# f = open('res/075778_treated_xye.csv', 'w')
# writer = csv.writer(f)
# writer.writerow('Q I Di')
# f.close()


# df = pd.read_csv("075773_treated_xye.csv", sep=',')
df = pd.read_csv("res/075777_treated_xye.csv", sep=',')
# df = pd.read_csv("095221_xye.csv", sep=';')
df.head()

print(df['Q'], df['I'],df['Di'])

df=df.dropna()

print(len(df['Q']), df['I'],df['Di'])



def f_model(x, a, c):
    return pd.np.exp(( x-a)**2 / c)

def background_f(x, a, c):
    return c*pd.np.exp(x*a)


df["model"] = background_f(df["Q"], 3, -2)
df['I'] = np.log(df['I'])
# df.head()

ax = df.plot(
    x="Q", y="I",
    kind="line", yerr="Di", title="Some experimetal data",
    linestyle="", marker=".",
    capthick=1, ecolor="gray", linewidth=1
)
# ax = df.plot(
#     x="Q", y="model",
#     kind="line", ax=ax, linewidth=1
# )

popt, pcov = curve_fit(
    f=background_f,  # model function
    xdata=df["Q"],   # x data
    ydata=df["I"],   # y data
    p0=(3, -2),      # initial value of the parameters
    sigma=df["Di"]   # uncertainties on y
)

print(popt)

df["model"] = background_f(df["Q"], popt[0], popt[1])
# ax = df.plot(
#     x="Q", y="model",
#     kind="line", ax=ax, linewidth=1
# )

df['difference'] =  df['I'] - df['model']


# plt.show()



## # # # # # # # # # # # # # # #

def thresholding_algo_median(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.median(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            # else:
            #     signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.median(filteredY[(i-lag+1):i+1])

            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.median(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))

def thresholding_algo_mean(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            # else:
            #     signals[i] = -1

            filteredY[i] = (1 - influence) * y[i] + influence  * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))

# Data


y = df['I']
# y = y[0:100]
y = savgol_filter(y, 20, 3, deriv=0)
# y = y[0:150]


# Settings: lag = 30, threshold = 5, influence = 0
lag = 10
threshold = 3
influence = 0

# Run algo with settings from above
result = thresholding_algo_mean(y, lag=lag, threshold=threshold, influence=influence)

# Plot result
pylab.subplot(211)
# pylab.plot(np.arange(1, len(y)+1), y, marker = 'o')
pylab.plot(np.arange(1, len(y)+1), y)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"], color="cyan", lw=2)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"] + threshold * result["stdFilter"], color="green", lw=2,)

pylab.plot(np.arange(1, len(y)+1),
           result["avgFilter"] - threshold * result["stdFilter"], color="green", lw=2,)

pylab.subplot(212)
pylab.step(np.arange(1, len(y)+1), result["signals"], color="red", lw=2)

print(result['signals'])
pylab.ylim(-1.5, 1.5)
pylab.show()





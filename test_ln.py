import pylab
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
import random
from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# df = pd.read_csv("data/095221_xye.csv", sep=';')
df = pd.read_csv("data/076022_treated_xye.csv", sep=',')

df = df.dropna()
# df = df[220:]
I_max = np.max(df['I'])
y = np.log(df['I']/I_max)

y = savgol_filter(y, 20, 3, deriv=0)

y_median = np.mean(y)

# plt.plot(y)

factor_reg = 1



def background_f(x, a, c):
    return c+x*a

def factor(x,a):
    return np.dot(a,x)

popt, pcov = curve_fit(
    f=background_f,       # model function
    xdata=df["Q"],   # x data
    ydata=y,   # y data
    p0=(-10, 4),      # initial value of the parameters
    sigma=df["Di"]   # uncertainties on y
)
# print(np.sqrt(np.diag(pcov)))
# print(popt)

df["model"] = background_f(df["Q"], popt[0], popt[1])
# print(df['model'])
plt.plot(np.arange(len(y)), y, np.arange(len(y)),factor(df['model'],factor_reg) )

surface = factor(df['model'],factor_reg)
# surface = surface[50:]

peaks, _ = find_peaks(y, height=surface, distance=5)
peaks = peaks[10:]
plt.plot(np.arange(len(y)), y, peaks, y[peaks],  "x")
plt.show()
print(peaks)

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


lag = 10
threshold = 3
influence = 0.1
# y = y[peaks]
# Run algo with settings from above
result = thresholding_algo_mean(y, lag=lag, threshold=threshold, influence=influence)

# Plot res
# pylab.subplot(211)
# # pylab.plot(np.arange(1, len(y)+1), y, marker = 'o')
# pylab.plot(np.arange(1, len(y)+1), y)
#
# pylab.plot(np.arange(1, len(y)+1),
#            result["avgFilter"], color="cyan", lw=2)
#
# pylab.plot(np.arange(1, len(y)+1),
#            result["avgFilter"] + threshold * result["stdFilter"], color="green", lw=2,)
#
# pylab.plot(np.arange(1, len(y)+1),
#            result["avgFilter"] - threshold * result["stdFilter"], color="green", lw=2,)
#
# pylab.subplot(212)
# pylab.step(np.arange(1, len(y)+1), result["signals"], color="red", lw=2)
#
# print(result['signals'])
# pylab.ylim(-1.5, 1.5)
# pylab.show()




f, (ax1, ax2, ax3) = plt.subplots(3, 1)

ax2.plot(np.arange(1, len(y)+1), y,
         np.arange(1, len(y)+1), result["avgFilter"],
         np.arange(1, len(y)+1),
                   result["avgFilter"] + threshold * result["stdFilter"],
         np.arange(1, len(y)+1),
                   result["avgFilter"] - threshold * result["stdFilter"],
         )
ax1.plot(np.arange(len(y)), y,
         np.arange(len(y)),factor(df['model'],factor_reg) ,
         np.arange(len(y)), y, peaks, y[peaks],  "x")
ax3.plot(np.arange(1, len(y)+1), result["signals"], color="red", lw=2)

plt.show()
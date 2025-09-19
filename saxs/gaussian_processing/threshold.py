import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.signal import medfilt

from settings_processing import EXTENSION

data = pd.read_csv("../" + "res/" + "075773_treated_xye" + EXTENSION, sep=",")

data = data.apply(pd.to_numeric, errors="coerce")
data = data.dropna()

q = np.array(data.iloc[:, 0])
I = np.array(data.iloc[:, 1])
dI = np.array(data.iloc[:, 2])


smoothed_data = medfilt(I, 3)
difference = np.abs(I - smoothed_data)
threshold = np.mean(difference) + 0.5 * np.std(difference)

noisy_indices = np.where(difference > threshold)[0]

first_part = gaussian_filter(I[: max(noisy_indices)], sigma=3)
sec_part = medfilt(I[max(noisy_indices) :], 3)
good_smoothed_without_loss = np.concatenate((first_part, sec_part))
good_smoothed_without_loss = medfilt(good_smoothed_without_loss, 3)


plt.plot(I, label="Original Data")
# plt.plot(smoothed_data, label='Smoothed Data')
plt.plot(good_smoothed_without_loss, label="GoodSm")
plt.legend()

plt.show()

plt.clf()
plt.plot(I, label="Original Data")

plt.plot(gaussian_filter(I, sigma=2), label="Gauss")
# plt.scatter(noisy_indices, I[noisy_indices], c='red', label='Noisy Part')
plt.legend()
plt.show()

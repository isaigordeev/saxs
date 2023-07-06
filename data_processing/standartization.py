import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

FILENAME = "075909_treated_xye"  # pointwise classification
EXTENSION = '.csv'
ANALYSE_DIR = '../results/'
DATA_DIR = '../res/'


data = pd.read_csv(DATA_DIR + FILENAME + EXTENSION, sep=',')
data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

q = np.array(data.iloc[:, 0])
I = np.array(data.iloc[:, 1])
dI = np.array(data.iloc[:, 2])

# q = q[200:]
# I = I[200:]
q = q/np.max(q)
mean = np.mean(I)
std = np.std(I)
norm_I = (I ) / std

I_filtered = savgol_filter(I, window_length=5, polyorder=0)



print(I[:5])
aI = I.reshape(1, len(I))
new_I = I.reshape(len(I), 1)


i = np.load("d_cubic.npy")
print(i)

# plt.plot( q, I, label = 'non_fil')
# plt.plot(q, I_filtered, label = 'si')
plt.plot(q, norm_I, label = 'standartised')
plt.legend()


# plt.savefig('test/standartization/' + FILENAME+'.pdf')
plt.show()


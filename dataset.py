import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from torch import nn
import torch
from scipy.signal import savgol_filter

FILENAME = "075775_treated_xye"  # pointwise classification
EXTENSION = '.csv'
ANALYSE_DIR = 'results/'
DATA_DIR = 'res/'

# Create a 2D array
array = np.random.rand(10, 10)

data = pd.read_csv(DATA_DIR + FILENAME + EXTENSION, sep=',')
data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

q = np.array(data.iloc[:, 0])
I = np.array(data.iloc[:, 1])[:300]
dI = np.array(data.iloc[:, 2])
I_filtered = savgol_filter(I, window_length=5, polyorder=0)
I = I_filtered


aI = I.reshape(1, len(I))
new_I = I.reshape(len(I), 1)


array = np.dot(new_I, aI)
max_pool_layer = nn.MaxPool2d(kernel_size=3)

array_sum = np.zeros((len(I), len(I)))
I_filtered = savgol_filter(I, window_length=5, polyorder=0)
# print(array_sum)

for x in range(len(I)):
    for y in range(len(I)):
        array_sum[x][y] = I[x]+I[y]


# print(len(array_sum[0]))
# print(len(array[0]))

tensor = torch.tensor(array)
# print(tensor.shape)
# max_pool_layer(tensor).unsqueeze(dim=1)
# Create a 2D image from the array

a = array
# a= max_pool_layer(tensor.unsqueeze(dim=0)).squeeze().numpy()
print(len(a[0]))
plt.imshow(a, cmap='gray')

# Show the image
plt.savefig('test/meshing/' + FILENAME+'.png')

# plt.plot(I, label='Original')
# plt.plot(I_filtered, label='Filtered')
# plt.legend()
# plt.show()
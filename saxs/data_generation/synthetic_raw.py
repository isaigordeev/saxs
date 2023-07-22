import json

import matplotlib.pyplot as plt
import numpy as np

from saxs.data_generation import DEFAULT_CONFIG_PATH
from saxs.data_generation.data_visualization import load_data

with open(DEFAULT_CONFIG_PATH) as config:
    config_data = json.load(config)

q, d1, d3, exp_data = load_data(phase=config_data['phase'],
                                cubic_mesophase=config_data['cubic_mesophase'])
data = np.load('Synthetic_raw/Im3m_cubic_raw.npy')


# print(x.shape)


# print(test_processing_data)
# print(d1.shape)
# print(test_processing_data[0][1][1])
for n in range(len(data))[:1]:
    x = data[n][1][1:]
    x = x / np.max(x)
    plt.plot(data[n][0][1:], x, 'o')
# plt.plot(q, d1[0], 'x')
# plt.plot(d)
plt.show()
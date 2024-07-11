import numpy as np
from matplotlib import pyplot as plt

# test_processing_data = np.load("../saxs_generated_data/G_cubic_raw_27.npy")
# print(test_processing_data.shape)
#
# for x in range(27):
#     plt.plot(test_processing_data[x][0][1:], test_processing_data[x][1][1:], 'ro')
#     plt.show()

data1 = np.load("../saxs_generated_data/G_cubic.npy")
data2 = np.load("../saxs_generated_data/cubic_q.npy")
print(data1.shape)
print(data2.shape)




for x in range(27):
    plt.imshow((data1[x]/np.min(data1[x])).astype(int))
    plt.show()

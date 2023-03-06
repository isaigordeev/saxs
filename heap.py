import numpy as np


I = np.array([1, 2, 3, 4, 5])

array_sum = I[:, np.newaxis] + I[np.newaxis, :]

print(array_sum)
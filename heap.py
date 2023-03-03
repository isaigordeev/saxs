import numpy as np

# create some sample data
I = np.array([1, 2, 3, 4, 5])

# compute the sum of all pairs of elements in I
array_sum = I[:, np.newaxis] + I[np.newaxis, :]

# display the result
print(array_sum)
# import json
#
# list = {'file1':{'name': 'John', 'age': 30, 'city': 'New York'},
#     'file2': {'name': 'John1', 'age': 30, 'city': 'New York'},
#         'file3': {'name': 'John1', 'age': 30, 'city': 'New York'},
#         'file4': {'name': 'John1', 'age': 30, 'city': 'New York'},
#         'file5': {'name': 'John1', 'age': 30, 'city': 'New York'},
#         'file6': {'name': 'John1', 'age': 30, 'city': 'New York'}}
#
#
# with open('data.json', 'w') as f:
#     json.dump(list, f, indent=4, separators=(",", ": "))
#
# with open('data.json', 'r') as f:
#     data = json.load(f)
# #
# # # print the data
# print(data['file1'])
import numpy as np
from fastdtw import fastdtw

# Define two time series
x = np.array([1, 2, 3, 4, 5])
y = np.array([1, 3, 5, 7, 9])
z = np.array(([1,4,5,8,10]))

# Compute the DTW distance and alignment
distance, path = fastdtw(x, y)
distance1, path1 = fastdtw(z, y)

print(distance)  # prints the DTW distance between x and y
print(path)
import matplotlib.pyplot as plt

# Plot the two time series and the alignment path
plt.plot(x, label='x')
plt.plot(y, label='y')
plt.plot(z, label='z')

for i, j in path:
    plt.plot([i, j, ], [x[i], y[j]], color='gray')
for i, j in path1:
    plt.plot([i, j], [z[i], y[j]], color='gray')
plt.legend()
plt.show()
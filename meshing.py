from matplotlib import pyplot as plt
import numpy as np


data = np.load("d_cubic.npy")
print(data)

# x = 1
# plt.plot( data[x][0], data[x][1], label = 'non_fil')
# plt.legend()
# plt.show()


num_subplots = 3

# Create the subplots
fig, axs = plt.subplots(num_subplots)

# Iterate over the subplots
# fig = plt.figure()

# Iterate over the subplots
num_subplots = 3


for i in range(1, num_subplots**2+1):
    # Create each subplot
    ax = plt.subplot(num_subplots, num_subplots, i)
    
    # Plot the data on each subplot
    ax.plot(data[i-1][0], data[i-1][1])
    # ax.plot(data[i-1][0], data[i-1][1], 'x')
    # ax.set_title('Subplot {}'.format(i+1))

plt.tight_layout()
# plt.savefig('test/standartization/' + FILENAME+'.pdf')
plt.show()
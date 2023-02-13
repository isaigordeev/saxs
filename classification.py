import random
from cmath import sqrt
import numpy as np

# import findPeaks

data = []

minq = 2
maxq = 6
N_peak = 10
trash_I = 1

la3d = [ 6, 8, 14, 16, 20, 22, 24, 26]
Pn3m = [ 2, 3, 4, 6, 8, 9, 10, 11, 12, 14, 16, 17]
Im3m = [ 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]

test = [random.uniform(minq - 1, +maxq + 1) for i in range(N_peak)]
test = sorted(test)


def ratio_lattice(seq):
    ratio_list = []
    for x in range(1, len(seq)):
        ratio_list.append(sqrt(seq[x])/sqrt(seq[x-1]))
    return ratio_list

ratio_list = []
def ratio_data(data):
    for x in range(1, len(data)-1):
        a = np.sqrt(data[x])/np.sqrt(data[0])
        print(a)

ratio_data(Im3m)
print(ratio_list)








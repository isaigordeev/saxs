import numpy as np
import pandas as pd
import os 
from settings import *
# import datetime


# now = datetime.datetime.now()
# filename_directory = analyse_directory + filename + str(now.time())[:8]

filename_directory = analyse_directory + filename

if not os.path.exists(filename_directory):
    os.mkdir(analyse_directory + filename)

data = pd.read_csv('res/' + filename+extension, sep=',')
data = data.apply(pd.to_numeric, errors='coerce')
data = data.dropna()

q = np.array(data.iloc[:, 0])
I = np.array(data.iloc[:, 1])
dI = np.array(data.iloc[:, 2])

delta_q = q[len(q) - 1] / len(q)
max_dI = np.median(dI)


def filtering_start_noise(q, I, dI):
    i = 0
    for x in q:
        i += 1
        if x > start:
            break
    return q[i:], I[i:], dI[i:]


q, I, dI = filtering_start_noise(q, I, dI)



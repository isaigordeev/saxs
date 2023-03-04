import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from torch import nn
import os 
import torch
from scipy.signal import savgol_filter
from PIL import Image
import random




FILENAME = "075775_treated_xye"  # pointwise classification
EXTENSION = '.csv'
SET_DIR_SUM = 'data/sum/'
SET_DIR_DOT = 'data/dot/'
DATA_DIR = 'res/'
START = 0.02

class_names = ['la3d', 'Pn3m', 'Im3m']

def get_filenames(folder_path):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            yield filename

def get_filenames_without_ext(folder_path):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Split the filename into name and extension, and return just the name
            name, extension = os.path.splitext(filename)
            if extension != '.txt':
                yield name


if not os.path.exists(SET_DIR_DOT):
    os.mkdir(SET_DIR_DOT)
if not os.path.exists(SET_DIR_SUM):
    os.mkdir(SET_DIR_SUM)

for x in class_names:
    if not os.path.exists(SET_DIR_SUM + x):
        os.mkdir(SET_DIR_SUM + x)
    if not os.path.exists(SET_DIR_DOT + x):
        os.mkdir(SET_DIR_DOT + x)



for filename in get_filenames_without_ext(DATA_DIR):
    data = pd.read_csv(DATA_DIR + filename + EXTENSION, sep=',')
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.dropna()


    q = np.array(data.iloc[:, 0])
    I = np.array(data.iloc[:, 1])
    dI = np.array(data.iloc[:, 2])

    # I_filtered = savgol_filter(I, window_length=5, polyorder=0)
    # I = I_filtered


    i = np.argmax(q > START)
    q, I, dI = q[i:], I[i:], dI[i:]





    array_dot = np.outer(I, I)
    array_sum = I[:, np.newaxis] + I[np.newaxis, :]


    # random.seed(1)
    plt.imshow(array_dot)
    plt.savefig(SET_DIR_DOT +  random.choice(class_names) +'/'+ filename + '.png')
    plt.clf()
    # random.seed(1)
    plt.imshow(array_sum)
    plt.savefig(SET_DIR_SUM + random.choice(class_names)+ '/'+ filename +  '.png')
    plt.clf()


import matplotlib.pyplot as plt
import numpy as np

from saxs.data_generation.processing import Processing
from saxs.data_generation.data_visualization import load_data, plot_saxs, plot_saxs_featuremap
from saxs.data_generation.generation import Generator
from saxs.data_generation import DEFAULT_CONFIG_PATH

import json

from saxs.gaussian_processing.processing_outils import read_data

with open(DEFAULT_CONFIG_PATH) as config:
    config_data = json.load(config)

if __name__ == '__main__':



    q, d1, d3, exp_data = load_data(phase=config_data['phase'],
                                    cubic_mesophase=config_data['cubic_mesophase'])

    q_0, I_0, dI = read_data('/Users/isaigordeev/Desktop/2023/saxs/res/075775_treated_xye.csv')
    data = np.load('/Users/isaigordeev/Desktop/2023/saxs/saxs/data_generation/Synthetic_raw/{}_cubic_raw.npy'.format(config_data['cubic_mesophase']))

    for n in range(len(d1)):
        # plot_saxs(q, d1[n])

        x = data[n][1][1:]
        x = x / np.max(x)
        plt.plot(data[n][0][1:], x, 'o')
        plt.plot(q_0, I_0/np.max(I_0), 'ro')
        plt.plot(q, d1[n]/np.max(d1[n]),)

        plt.show()


    # plot_saxs(q, d1[0])


    # plt.figure()
    # plt.plot(q,10*d1[0])
    # plt.plot(q_0, I_0)
    # plt.xlabel('q')
    # plt.ylabel('Intensity')
    # plt.show()


    # plt.plot()

    # plot_saxs_umap(d1,exp_data)
    # plot_saxs_tsne(d1,exp_data)
    # plot_saxs_pca(d1,exp_data)
    print(d1.shape)
    print(d3.shape)
    # print(d3[])
    # plot_saxs()
        # print(x)
    # plot_saxs_featuremap(d3[0],q)
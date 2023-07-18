from saxs.data_generation.processing import Processing
from saxs.data_generation.data_visualization import load_data, plot_saxs, plot_saxs_featuremap
from saxs.data_generation.generation import Generator
from saxs.data_generation import DEFAULT_CONFIG_PATH

import json


with open(DEFAULT_CONFIG_PATH) as config:
    config_data = json.load(config)

if __name__ == '__main__':

    # generator = Generator(phase=config_data['phase'],
    #                       cubic_mesophase=config_data['cubic_mesophase'],
    #                       len_num=config_data['len_num'],
    #                       lat_num=config_data['lat_num'],
    #                       sigma_num=config_data['sigma_num'],
    #                       params=config_data['params'],
    #                       )
    #
    # generator.generation()
    processing = Processing()
    processing.process()
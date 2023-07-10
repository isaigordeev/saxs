from processing import Processing
from data_visualization import load_data, plot_saxs, plot_saxs_featuremap
from generation import Generator
import json

# import argparse
# parser = argparse.ArgumentParser(description='Phase visualization')
#
# parser.add_argument('-phase', '-p',  help='phase_to_visualize')
# parser.add_argument('--cubic_mesophase', '--ph', help='cubic_mesophase')
#
# args = parser.parse_args()
#
# phase = args.phase
# cubic_mesophase = args.cubic_mesophase

with open('config.json') as config:
    config_data = json.load(config)

if __name__ == '__main__':

    generator = Generator(phase=config_data['phase'],
                          cubic_mesophase=config_data['cubic_mesophase'],
                          len_num=config_data['len_num'],
                          lat_num=config_data['lat_num'],
                          sigma_num=config_data['sigma_num'],
                          params=config_data['params'],
                          )

    generator.generation()
    processing = Processing()
    processing.process()


    phase = 'cubic'
    cubic_mesophase = 'la3d'
    q, d1, d3, exp_data = load_data(phase=phase,
                                    cubic_mesophase=cubic_mesophase)
    for x in range(len(d1)):
        plot_saxs(d1[x],q)


    # # plot_saxs_umap(d1,exp_data)
    # # plot_saxs_tsne(d1,exp_data)
    # # plot_saxs_pca(d1,exp_data)
    # print(d1.shape)
    # print(d3.shape)
    # # print(d3[])

        # print(x)
    # plot_saxs_featuremap(d3[0],q)
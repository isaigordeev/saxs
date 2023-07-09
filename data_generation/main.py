from data_visualization import load_data, plot_saxs
import argparse

parser = argparse.ArgumentParser(description='Phase visualization')

parser.add_argument('-phase', help='phase_to_visualize')
parser.add_argument('--cubic_mesophase', '--mph', help='cubic_mesophase')

args = parser.parse_args()

phase = args.phase
cubic_mesophase = args.cubic_mesophase


if __name__ == '__main__':
    Phase = 'cubic'
    d1, d3, exp_data, q = load_data(phase=phase,
                                    cubic_mesophase=cubic_mesophase)
    # plot_saxs_umap(d1,exp_data)
    # plot_saxs_tsne(d1,exp_data)
    # plot_saxs_pca(d1,exp_data)

    for x in range(len(d1)):
        plot_saxs(d1[x],q)
    # plot_saxs_featuremap(d3[0],q)
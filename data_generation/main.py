from data_visualization import load_data, plot_saxs, plot_saxs_featuremap
import argparse

parser = argparse.ArgumentParser(description='Phase visualization')

parser.add_argument('-phase', help='phase_to_visualize')
parser.add_argument('--cubic_mesophase', '--mph', help='cubic_mesophase')

args = parser.parse_args()

phase = args.phase
cubic_mesophase = args.cubic_mesophase


if __name__ == '__main__':
    q, d1, d3, exp_data = load_data(phase=phase,
                                    cubic_mesophase=cubic_mesophase)
    # plot_saxs_umap(d1,exp_data)
    # plot_saxs_tsne(d1,exp_data)
    # plot_saxs_pca(d1,exp_data)

    print(d3.shape)
    # print(d3[])
    for x in range(len(d1)):
        plot_saxs(d1[x],q)
        # print(x)
    plot_saxs_featuremap(d3[0],q)
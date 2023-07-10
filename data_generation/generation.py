import sys
import os

from generation_settings import bijection_name, core_path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import saxspy
import matplotlib.pyplot as plt
import numpy as np
# Instantiate the synthetic model: 'P', 'G', or 'D'
import argparse



parser = argparse.ArgumentParser(description='Phase for generation')

parser.add_argument('-phase', help='Phase for generation')
parser.add_argument('--cubic_mesophase', '--mph', help='cubic_mesophase if cubic phase entered')

args = parser.parse_args()

phase = args.phase
cubic_mesophase = args.cubic_mesophase

class Generator:
    def __init__(self, phase,
                 params=np.array([[10, 60], [0.8, 2], [0.04, 0.1]]),
                 lat_num=1,
                 let_num=1,
                 sigma_num=1,
                 cubic_mesophase=None,
                 save_path=os.path.dirname(__file__)):

        assert phase == 'cubic' or phase == 'lamellar' or phase == 'hexagonal'

        self.phase = phase
        self.cubic_mesophase = cubic_mesophase
        self.params = params
        self.lat_num = lat_num
        self.length_num = let_num
        self.sigma_num = sigma_num
        self.save_path = os.path.join(save_path, 'Synthetic_raw')


    def generation(self):
        if self.phase == 'cubic':
            if self.cubic_mesophase is not None:
                assert self.cubic_mesophase == 'Im3m' or self.cubic_mesophase == 'la3d' or self.cubic_mesophase == 'Pn3m' or \
                       self.cubic_mesophase == 'P' or self.cubic_mesophase == 'G' or self.cubic_mesophase == 'D'

                if len(self.cubic_mesophase) == 1:
                    cubic_mesophase = bijection_name[self.cubic_mesophase]

                print(f"running cubic {self.cubic_mesophase} model...")
                cm = saxspy.CubicModel(self.cubic_mesophase)

                #----------------------- generate synthetic data -----------------------#
                # ranges of: lattice parameter, length of lipid, lipid head sigma

                # params = np.array([[28, 40], [0.2, 0.5], [0.5, 1]])  #good but lattice parameter
                # params = np.array([[10, 40], [0.07, 0.1], [0.1, 0.4]]) #good for Im3m

                # params = np.array([[10, 40], [0.15, 0.20], [0.01, 0.1]]) # good for 10 0.15 0.01 P
                # params = np.array([[10, 40], [0.15, 0.17], [0.04, 0.06]]) # good for 10 0.15 0.04 P


                # params10 = np.array([[10, 10], [0.13, 0.17], [0.02, 0.06]])

                # params40 = [[value * 4 for value in sublist] for sublist in params10]
                # print(params40)



                store_it = cm.generateSynthCubic(self.params, self.lat_num, self.length_num, self.sigma_num)

                current_file_path = os.path.dirname(__file__)
                print(current_file_path)
                current_directory = os.getcwd()
                print(current_directory)
                # current_file_path = os.path.abspath(__file__)
                # parent_directory = os.path.dirname(current_file_path)
                # print(parent_directory)

                filename = '{}_cubic_raw.npy'.format(self.cubic_mesophase)
                self.save_path = os.path.join(self.save_path, filename)

                print(self.save_path)
                np.save(self.save_path, store_it)

            else: raise AttributeError('Enter cubic mesophase:  -phase \'cubic\' --mph \'Im3m\'')
        elif self.phase == 'lamellar':
            pass
        elif self.phase == 'hexagonal':
            pass

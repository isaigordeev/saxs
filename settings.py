import numpy as np

# to be implemented unique for each data + manual adjusting
START = 0.02
BACKGROUND_COEF = 0.7
SIGMA_FILTER = 1.5
SIGMA_FITTING = 0.3
TRUNCATE = 4
PROMINENCE = 0.6
INFINITY = 100

FILENAME = "075966_treated_xye"  # pointwise classification
EXTENSION = '.csv'
ANALYSE_DIR = 'results/'
ANALYSE_DIR_SESSIONS = ANALYSE_DIR + 'sessions/'
ANALYSE_DIR_SESSIONS_RESULTS = ANALYSE_DIR + 'sessions_results/'
DATA_DIR = 'data_test/'

# phases
class_names = ['la3d', 'Pn3m', 'Im3m']
class_to_dict = {class_names[x]:x for x in range(len(class_names))}

la3d = np.array([6, 8, 14, 16, 20, 22, 24, 26]).astype(float)
Pn3m = np.array([2, 3, 4, 6, 8, 9, 10, 11, 12, 14, 16, 17]).astype(float)
Im3m = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]).astype(float)

defined_phases = np.array([np.sqrt(la3d),
                           np.sqrt(Pn3m),
                           np.sqrt(Im3m)],
                          dtype=object)

import numpy as np

# to be implemented unique for each data + manual adjusting
START = 0.02
BACKGROUND_COEF = 0.7 #normal 0.7
SIGMA_FILTER = 1.5
SIGMA_FITTING = 0.3
TRUNCATE = 4
PROMINENCE = 0.6
INFINITY = 100
WINDOWSIZE = 6
RESOLUTION_FACTOR = 1.4

FILENAME = "075966_treated_xye"  # pointwise classification
EXTENSION = '.csv'
ANALYSE_DIR = 'results/'
PHASES_DIR = 'phases.json'
ANALYSE_DIR_SESSIONS = ANALYSE_DIR + 'sessions/'
ANALYSE_DIR_SESSIONS_RESULTS = ANALYSE_DIR + 'sessions_results/'
DATA_DIR = 'data_test/'
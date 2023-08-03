import json
import os

import numpy as np


from saxs.gaussian_processing.settings_processing import ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS


class AbstractPhaseKernel:
    def __init__(self, sample, data, phases_dict, phases_coefficients):

        self.phases_coefficients = phases_coefficients
        self.phases_dict = phases_dict
        self.data = data
        self.sample = sample
        self.analyzed_q = np.array([])

        self.phases_number = len(self.phases_coefficients)
        self.distances = np.zeros(self.phases_number)

    def __call__(self, *args, **kwargs):
        return self.phase_classification()

    def set_directories(self, sample_name):
        self.filename_analyse_dir_phases = '../' + ANALYSE_DIR_SESSIONS + sample_name + '/phases'

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)

    def preprocessing_q(self):
        self.preprocessed_q = self.analyzed_q / self.analyzed_q[0]
        self.preprocessed_q = self.preprocessed_q[1:]


    def phase_classification(self):
        # self.set_directories(sample_name)
        self.read_sample_data()

        if len(self.analyzed_q) > 1:
            self.phase_processing()

            return self.phases_dict[np.argmax(self.distances)]
        elif len(self.analyzed_q) == 1:
            return 'lamellar'
        else:
            return 'blanc'

    def phase_processing(self):
        pass

    def read_sample_data(self):
        self.analyzed_q = self.data[self.sample]['q']
        self.analyzed_q = np.array(self.analyzed_q)


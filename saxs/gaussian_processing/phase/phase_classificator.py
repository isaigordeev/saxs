import json
import os

import numpy as np

from saxs.gaussian_processing.processing_outils import calculate_absolute_difference

from saxs.gaussian_processing.phase.abstr_phase import AbstractPhaseClassificator
from saxs.gaussian_processing.settings_processing import ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS

class DefaultPhaseClassificator(AbstractPhaseClassificator):
    def __init__(self, current_session, data_directory=None):
        super().__init__(current_session, data_directory)

        self.filename_analyse_dir_phases = ''
        self.sample_data = {}

        self.q = np.array([])
        self.preprocessed_q = np.array([])
        self.distances = np.zeros(self.phases_number)


        if self.data_directory is ANALYSE_DIR_SESSIONS_RESULTS:
            self.data_directory += (self.current_date_session + self.current_time + '.json')

        self.read_data()


    def set_directories(self, sample_name):
        self.filename_analyse_dir_phases = '../'+ ANALYSE_DIR_SESSIONS + sample_name + '/phases'

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)


    def read_data(self):
        with open(self.data_directory, 'r') as file:  # NOTE make it better with string formatting
            self.data = json.load(file)

    def read_sample_data(self, sample_name):   #better return?
        self.sample_data = self.data[sample_name]
        self.q = np.array(self.sample_data['q'])

    def q_preprocessing(self):
        self.preprocessed_q = self.q/self.q[0]
        self.preprocessed_q = self.preprocessed_q[1:]

    def absolute_sequence_comparison(self):
        for i in range(self.phases_number):
            self.distances[i] = calculate_absolute_difference(self.phases_coefficients[i], self.preprocessed_q)

        # print(self.preprocessed_q)
        # print(self.distances)

    def point_classification(self, sample_name):
        # self.set_directories(sample_name)
        self.read_sample_data(sample_name)
        if len(self.q) > 1:
            self.q_preprocessing()
            self.absolute_sequence_comparison()
            self.data[sample_name]['phase'] = self.phases_dict[np.argmax(self.distances)]
            self.write_data(sample_name)
        elif len(self.q) == 1:
            self.data[sample_name]['phase'] = 'lam'
            self.write_data(sample_name)
        else:
            self.data[sample_name]['phase'] = 'blanc'
            self.write_data(sample_name)


    def directory_classification(self, sample_names=None, directory=None): #dir?
        if sample_names is not None:
            for sample in sample_names:
                # print(sample)
                self.point_classification(sample)
        else:
            for sample in self.data.keys():
                self.point_classification(sample)

    def write_data(self, sample_name):
        # print(self.phases_dict[np.argmax(self.distances)])
        with open(self.data_directory, 'w') as f:
            json.dump(self.data, f, indent=4, separators=(",", ": "))




# from settings_processing import *
# from datetime import date, datetime
# #
# #
# #
# now = datetime.now()
#
# today = now.today().date()
# print(today)
# current_time = now.strftime("%H:%M:%S")

# works
# b = DefaultPhaseClassificator('../' + ANALYSE_DIR_SESSIONS_RESULTS + '2023-07-06/' + '04:59:02.json', now)
# b.classification('075776_treated_xye')

# b = DefaultPhaseClassificator(now, ANALYSE_DIR_SESSIONS_RESULTS + '2023-07-07/' + '01:26:01.json')
# b.directory_classification()






import json
import os

import numpy as np

from outils.outils import calculate_absolute_difference
from saxs_processing.abstr_phase import AbstractPhaseClassificator
from settings_processing import ANALYSE_DIR_SESSIONS


class DefaultPhaseClassificator(AbstractPhaseClassificator):
    def __init__(self, data_directory, current_session, ):
        super().__init__(data_directory, current_session)

        self.filename_analyse_dir_phases = ''
        self.sample_data = {}

        self.q = np.array([])
        self.preprocessed_q = np.array([])

        self.distances = np.zeros(self.phases_number)

    def set_directories(self, sample_name):
        self.filename_analyse_dir_phases = ANALYSE_DIR_SESSIONS + sample_name + '/phases'

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)


    def read_sample_data(self, sample_name):   #better return?
        self.sample_data = self.data[sample_name]
        self.q = np.array(self.sample_data['q'])

    def q_preprocessing(self):
        self.preprocessed_q = self.q/self.q[0]
        self.preprocessed_q = self.preprocessed_q[1:]
    def absolute_sequence_comparison(self):
        for i in range(self.phases_number):
            self.distances[i] = calculate_absolute_difference(self.phases_coefficients[i], self.preprocessed_q)

        print(self.preprocessed_q)
        print(self.distances)
    def classification(self, sample_name):
        # self.set_directories(sample_name)
        self.read_sample_data(sample_name)
        self.q_preprocessing()
        self.absolute_sequence_comparison()


from settings_processing import *
from datetime import date, datetime


today = date.today()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

b = DefaultPhaseClassificator('../' + ANALYSE_DIR_SESSIONS_RESULTS + '2023-07-06/' + '04:59:02.json', now)
b.classification('075776_treated_xye')






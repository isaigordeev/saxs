import os

import numpy as np

from saxs.application.settings_processing import (
    ANALYSE_DIR_SESSIONS,
)


class AbstractPhaseKernel:
    def __init__(self, sample, data, phases_dict, phases_coefficients):
        self.phases_coefficients = phases_coefficients
        self.phases_dict = phases_dict
        self.data = data
        self.sample = sample
        self.analyzed_q = np.array([])

        self.phases_number = len(self.phases_coefficients)
        self.distances = np.zeros(self.phases_number)

        assert data is not None

    def __call__(self, *args, **kwargs):
        return self.phase_classification()

    def set_directories(self, sample_name) -> None:
        self.filename_analyse_dir_phases = (
            "../" + ANALYSE_DIR_SESSIONS + sample_name + "/phases"
        )

        if not os.path.exists(self.filename_analyse_dir_phases):
            os.mkdir(self.filename_analyse_dir_phases)

    def default_preprocessing_q(self) -> None:
        self.preprocessed_q = self.analyzed_q / self.analyzed_q[0]
        self.preprocessed_q = self.preprocessed_q[1:]

    def phase_classification(self):
        # self.set_directories(sample_name)
        self.read_sample_data()

        if self.analyzed_q is None:
            return "blanc"
        if len(self.analyzed_q) > 1:
            self.phase_processing()

            return self.phases_dict[np.argmax(self.distances)]
        if len(self.analyzed_q) == 1:
            return "lamellar"
        return "blanc"

    def phase_processing(self) -> None:
        pass

    def read_sample_data(self) -> None:
        if self.data[self.sample]["q"] is not None:
            self.analyzed_q = self.data[self.sample]["q"]
            self.analyzed_q = np.array(self.analyzed_q)
        else:
            self.analyzed_q = None

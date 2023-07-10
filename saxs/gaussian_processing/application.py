import json
import os

from .processing_classificator import AbstractProcessing, Application
from .abstr_peak import AbstractPeakClassificator
from .abstr_phase import AbstractPhaseClassificator
from .settings_processing import ANALYSE_DIR_SESSIONS_RESULTS, ANALYSE_DIR_SESSIONS, ANALYSE_DIR


class ApplicationManager(Application):
    def __init__(self,
                 current_session,
                 peak_classificator: AbstractPeakClassificator = None,
                 phase_classificator: AbstractPhaseClassificator = None,
                 custom_output_directory=None
                 ) -> None:
        super().__init__(current_session, custom_output_directory)

        self.data = {}
        self.files_number = 0
        self.peak_classificator = peak_classificator
        self.phase_classificator = phase_classificator
        self.custom_output_directory = custom_output_directory

        self.write_data()  # create json

    def write_data(self):
        write_json_path = os.path.join(self.current_results_dir_sessions, '{}.json'.format(self.current_time))

        with open(write_json_path, 'w') as f:
            json.dump(self.data, f)

    def point_processing(self, sample):
        pass

    def directory_processing(self):
        self.directory_peak_processing()
        self.directory_phase_processing()

    def point_peak_processing(self, sample):
        pass

    def point_phase_processing(self, sample):
        pass

    def directory_peak_processing(self):
        pass

    def directory_phase_processing(self):
        pass

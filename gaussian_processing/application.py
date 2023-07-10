import json
import os

from .processing_classificator import AbstractProcessing
from .abstr_peak import AbstractPeakClassificator
from .abstr_phase import AbstractPhaseClassificator
from .settings_processing import ANALYSE_DIR_SESSIONS_RESULTS, ANALYSE_DIR_SESSIONS, ANALYSE_DIR


class ApplicationManager(AbstractProcessing):
    def __init__(self,
                 current_session,
                 peak_classificator: AbstractPeakClassificator = None,
                 phase_classificator: AbstractPhaseClassificator = None,
                 custom_output_directory=None
                 ) -> None:
        super().__init__(current_session)

        self.data = {}
        self.files_number = 0
        self.peak_classificator = peak_classificator
        self.phase_classificator = phase_classificator
        self.custom_output_directory = custom_output_directory

        self.analysis_dir = None
        self.analysis_dir_sessions = None
        self.results_dir_sessions = None
        self.current_results_dir_sessions = None

        self.executing_path = os.getcwd()

        self.set_directories()
        self.write_data()  # create json

    def set_directories(self):

        if self.custom_output_directory is None:
            self.analysis_dir = os.path.join(self.executing_path, ANALYSE_DIR)
            self.analysis_dir_sessions = os.path.join(self.analysis_dir, ANALYSE_DIR_SESSIONS)
            self.results_dir_sessions = os.path.join(self.analysis_dir, ANALYSE_DIR_SESSIONS_RESULTS)
            self.current_results_dir_sessions = os.path.join(self.results_dir_sessions, self.current_date_session)
        else:
            # analysis_dir = os.path.join(self.custom_output_directory, ANALYSE_DIR)
            # analysis_dir_sessions = ANALYSE_DIR_SESSIONS
            # results_dir_sessions = ANALYSE_DIR_SESSIONS_RESULTS
            #
            # if not os.path.exists(self.custom_output_directory):
            #     os.mkdir(self.custom_output_directory)
            pass

        if not os.path.exists(self.analysis_dir):
            os.mkdir(self.analysis_dir)
        if not os.path.exists(self.analysis_dir_sessions):
            os.mkdir(self.analysis_dir_sessions)
        if not os.path.exists(self.results_dir_sessions):
            os.mkdir(self.results_dir_sessions)
        if not os.path.exists(self.current_results_dir_sessions):
            os.mkdir(self.current_results_dir_sessions)

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
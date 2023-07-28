import json
import os
from typing import Any

from .processing_classificator import Application
from saxs.gaussian_processing.peak.peak_application import PeakApplication
from saxs.gaussian_processing.phase.phase_application import PhaseApplication


class ApplicationManager(Application):
    def __init__(self,
                 current_session=None,
                 peak_kernel: PeakApplication = None,
                 phase_kernel: PhaseApplication= None,
                 custom_output_directory=None
                 ) -> None:
        super().__init__(current_session, custom_output_directory)


        self.data = {}
        self.files_number = 0
        self.peak_kernel = peak_kernel
        self.phase_kernel = phase_kernel
        self.custom_output_directory = custom_output_directory

        self.peak_classification = True if self.peak_kernel is not None else False
        self.phase_classification = True if self.phase_kernel is not None else False

        # self.set_directories()
        self.write_data()  # create json


    def write_data(self):
        write_json_path = os.path.join(self._current_results_dir_session, '{}.json'.format(self.current_time))
        with open(write_json_path, 'w') as f:
            json.dump(self.data, f)

    def point_peak_processing(self, sample):
        pass

    def point_phase_processing(self, sample):
        pass

    def directory_peak_processing(self):
        pass

    def directory_phase_processing(self):
        pass

    def point_processing(self, sample):
        pass


    def directory_processing(self):
        self.directory_peak_processing()
        self.directory_phase_processing()

    def custom_directory_processing(self):
        self.custom_process()

    def custom_process(self):
        pass

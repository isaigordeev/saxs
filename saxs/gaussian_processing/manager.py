import time
from typing import Any

from saxs.gaussian_processing.phase.abstr_phase import PhaseApplication
from saxs.gaussian_processing.peak.peak_application import PeakApplication
from .application import ApplicationManager

time_start1 = time.time()

import os

from datetime import datetime

time_start2 = time.time()

now = datetime.now()

today = now.today().date()


# current_time = now.strftime("%H:%M:%S")
#
# current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'
# current_session_results = ANALYSE_DIR_SESSIONS_RESULTS + str(today) + '/'

# if not os.path.exists(current_session):
#     os.mkdir(current_session)
# if not os.path.exists(current_session_results):
#     os.mkdir(current_session_results)





class Manager(ApplicationManager):
    def __init__(self,
                 peak_data_directory='test_processing_data/',
                 phase_data_directory=None,
                 peak_kernel: PeakApplication=None,
                 phase_kernel: PhaseApplication=None,
                 current_session=None) -> None:

        super().__init__(current_session=current_session,
                         peak_kernel=peak_kernel,
                         phase_kernel=phase_kernel)

        self.peak_data_directory = os.path.join(self.executing_path, peak_data_directory)

        self.is_peak_data_directory = os.path.isdir(peak_data_directory)
        self.is_phase_data_directory = os.path.isdir(phase_data_directory)


        if phase_data_directory is not None:
            self.phase_data_directory = phase_data_directory
        else:
            self.phase_data_directory = self._current_results_dir_session




    def __call__(self, *args: Any, **kwds: Any) -> Any:

        if self.peak_classification:
            if self.is_peak_data_directory:
                self.directory_peak_processing()
            else: self.point_peak_processing()
        if self.phase_classification:
            self.directory_phase_processing()

        return super().__call__(*args, **kwds)

    def point_peak_processing(self):
        directory_peak_classificator = self.peak_kernel(data_directory=self.peak_data_directory)
        print('POINT {} PEAK CLASSIFICATION'.format(directory_peak_classificator.data_directory))

    def directory_peak_processing(self):
        directory_peak_classificator = self.peak_kernel(data_directory=self.peak_data_directory)
        print('DIRECTORY {} PEAK CLASSIFICATION'.format(directory_peak_classificator.data_directory))

        directory_peak_classificator.directory_classification()

    def print_data(self):
        print(self.data)

    def directory_phase_processing(self):
        directory_phase_classificator = self.phase_kernel(data_directory=self.phase_data_directory)
        print('DIRECTORY {} PHASE CLASSIFICATION'.format(directory_phase_classificator.data_directory))

        directory_phase_classificator.directory_classification()

    def custom_process(self, filename):
        peaks = self.peak_classificator(current_session=self.current_session,
                                        filename=filename,
                                        data_directory=self.peak_data_directory)
        peaks.filtering()
        peaks.denoising()
        peaks.custom_filtering_()


class Custom_Manager(Manager):
    def __init__(self, peak_classificator,
                 phase_classificator,
                 current_session,
                 peak_data_directory,
                 phase_data_directory):
        super().__init__(current_session=current_session,
                         peak_classificator=peak_classificator,
                         phase_classificator=phase_classificator,
                         peak_data_directory=peak_data_directory,
                         phase_data_directory=phase_data_directory)

    def point_peak_processing(self, filename):
        peaks = self.peak_classificator(current_session=self.current_session,
                                        filename=filename,
                                        data_directory=self.peak_data_directory)
        

        # peaks.denoising()
        peaks.prefiltering()
        peaks.background_reduction()
        # peaks.filtering_negative()
        peaks.setting_state()
        # peaks.custom_filtering_()
        peaks.filtering_negative()
        peaks.background_plot()  # for main
        # peaks.peak_searching(height=0, prominence=PROMINENCE, distance=6)
        peaks.current_state_plot()  # for main
        # peaks.custom_peak_fitting_with_parabole(0)
        peaks.peak_processing()
        # peaks.custom_peak_fitting(0)
        # peaks.peak_substraction(0)
        peaks.current_state_plot()  # for main
        peaks.result_plot()  # for main

        # for x in range(len(peaks.peaks)):
        #     peaks.custom_peak_fitting_with_parabole(x)
        self.data[filename] = peaks.gathering()
        # self.files_number += 1
        # print(peaks.peaks_data)

        peaks.postprocessing()
        peaks.write_data()

        if self.data[filename]['peak_number'] == 0:
            pass

        # print(peaks.deltas)
        # print(peaks.test_processing_data)
        # print(sorted(peaks.peaks_analysed_q/min(peaks.peaks_analysed_q)))

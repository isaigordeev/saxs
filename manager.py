import time

from saxs_processing.p_peak_classification import PPeaks

time_start1 = time.time()

import argparse
import json
import os

from datetime import datetime

from settings_processing import ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS, DATA_DIR, PROMINENCE, ANALYSE_DIR
from saxs_processing.abstr_peak import PeakClassificator

from saxs_processing.custom_peak_classification import Peaks

# from saxs_processing.phase_classification import

time_start2 = time.time()

now = datetime.now()
today = now.today().date()

current_time = now.strftime("%H:%M:%S")

current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'
current_session_results = ANALYSE_DIR_SESSIONS_RESULTS + str(today) + '/'

# if not os.path.exists(current_session):
#     os.mkdir(current_session)
# if not os.path.exists(current_session_results):
#     os.mkdir(current_session_results)


def get_filenames(folder_path):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            yield filename


def get_filenames_without_ext(folder_path):
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
                name, extension = os.path.splitext(filename)
                if (name != '.DS_Store'):
                    yield name


class ApplicationManager:
    def __init__(self, current_session,  _class: PeakClassificator, DATA_DIR=DATA_DIR, custom_directory=None) -> None:
        self.DATA_DIR = DATA_DIR


        self.current_session = current_session
        self.current_date_session = str(current_session.today().date()) + '/'
        self.current_time = current_session.strftime("%H:%M:%S")

        self.data = {}
        self.files_number = 0
        self._class = _class

        self.custom_directory = custom_directory
        self.set_directories()
        self.write_data()

    def set_directories(self):

        if self.custom_directory is None:
            analysis_dir_sessions = ANALYSE_DIR_SESSIONS
            results_dir_sessions = ANALYSE_DIR_SESSIONS_RESULTS

            if not os.path.exists(ANALYSE_DIR):
                os.mkdir(ANALYSE_DIR)
            if not os.path.exists(analysis_dir_sessions):
                os.mkdir(analysis_dir_sessions)
            if not os.path.exists(results_dir_sessions):
                os.mkdir(results_dir_sessions)
            if not os.path.exists(results_dir_sessions + self.current_date_session):
                os.mkdir(results_dir_sessions + self.current_date_session)

        else:
            if not os.path.exists(self.custom_directory):
                os.mkdir(self.custom_directory)

    def write_data(self):
        with open(ANALYSE_DIR_SESSIONS_RESULTS + self.current_date_session + self.current_time + '.json', 'w') as f:
            json.dump(self.data, f)

    def atomic_processing(self, filename):
        pass

    def repo_processing(self, filename):
        pass

class Manager(ApplicationManager):
    def __init__(self, current_session,  _class, DATA_DIR=DATA_DIR) -> None:
        super().__init__(current_session, _class, DATA_DIR)

    def atomic_processing(self, filename):
        peaks = self._class(filename, self.DATA_DIR, current_session=self.current_session)
        peaks.background_reduction()
        peaks.custom_filtering()
        peaks.background_plot()
        peaks.filtering_negative()
        peaks.peak_processing()

        if peaks.peak_number == 0:
            pass

        peaks.result_plot()


        self.data[filename] = peaks.gathering()
        # peaks.custom_total_fit()
        # peaks.sum_total_fit()

        self.files_number += 1
        print('Finished ' + filename + ' ' + str(self.files_number))
        # phase TODO

    def repo_processing(self):
        filenames = get_filenames_without_ext(self.DATA_DIR)
        for filename in filenames:
            self.atomic_processing(filename)


    def print_data(self):
        print(self.data)


class Custom_Manager(Manager):
    def __init__(self, _class, current_session, DATA_DIR=DATA_DIR, ):
        super().__init__(current_session, _class, DATA_DIR=DATA_DIR)


    def atomic_processing(self, filename):
        peaks = self._class(filename, self.DATA_DIR, current_session=self.current_session)
        peaks.prefiltering()
        peaks.background_reduction()
        peaks.setting_state()
        # peaks.custom_filtering_()
        peaks.background_plot()
        peaks.filtering_negative()
        # peaks.peak_searching(height=0, prominence=PROMINENCE, distance=6)
        peaks.state_plot()
        # peaks.custom_peak_fitting_with_parabole(0)
        peaks.peak_processing()
        # peaks.custom_peak_fitting(0)
        # peaks.peak_substraction(0)
        peaks.state_plot()
        peaks.result_plot()

        # for x in range(len(peaks.peaks)):
        #     peaks.custom_peak_fitting_with_parabole(x)
        self.data[filename] = peaks.gathering()
        self.files_number += 1
        # print(peaks.peaks_data)

        if self.data[filename]['peak_number'] == 0:
            pass

        peaks.write_data()

        print(peaks.deltas)
        print(peaks.data)
        print(sorted(peaks.peaks_analysed_q/min(peaks.peaks_analysed_q)))


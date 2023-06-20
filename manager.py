import time
time_start1 = time.time()

import argparse
import json
import os

from datetime import datetime

from settings import ANALYSE_DIR_SESSIONS, ANALYSE_DIR_SESSIONS_RESULTS, DATA_DIR, PROMINENCE
from saxs_processing.abstr_peak import PeakClassificator

from saxs_processing.custom_peak_classification import Peaks

# from saxs_processing.phase_classification import

time_start2 = time.time()

now = datetime.now()
today = now.today().date()

current_time = now.strftime("%H:%M:%S")

current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'
current_session_results = ANALYSE_DIR_SESSIONS_RESULTS + str(today) + '/'

if not os.path.exists(current_session):
    os.mkdir(current_session)
if not os.path.exists(current_session_results):
    os.mkdir(current_session_results)


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


data = {}
files_number = 0

class ApplicationManager:
    def __init__(self, current_session: str,  _class, DATA_DIR=DATA_DIR) -> None:
        self.DATA_DIR = DATA_DIR
        self.current_session = current_session
        self.data = {}
        self.files_number = 0
        self._class = _class

    def atomic_processing(self, filename):
        pass

    def repo_processing(self, filename):
        pass

class Manager(ApplicationManager):
    def __init__(self, current_session: str,  _class = Peaks, DATA_DIR=DATA_DIR) -> None:
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
        peaks.custom_total_fit()
        peaks.sum_total_fit()

        self.files_number += 1
        print('Finished ' + filename + ' ' + str(self.files_number))
        # phase TODO

    def repo_processing(self):
        filenames = get_filenames_without_ext(self.DATA_DIR)
        for filename in filenames:
            self.atomic_processing(filename)


    def print_data(self):
        print(self.data)

    def write_data(self):
        with open(current_session_results + current_time + f'_{self.files_number}.json', 'w') as f:
            json.dump(self.data, f, indent=4, separators=(",", ": "))


class Custom_Manager(Manager):
    def __init__(self, current_session: str, DATA_DIR=DATA_DIR, _class=Peaks):
        super().__init__(current_session, _class, DATA_DIR=DATA_DIR)

    def custom_repo_processing(self):
        filenames = get_filenames_without_ext(self.DATA_DIR)
        for filename in filenames:
            self.custom_atomic_processing(filename)

    def custom_atomic_processing(self, filename):
        peaks = self._class(filename, self.DATA_DIR, current_session=self.current_session)
        peaks.background_reduction()
        peaks.custom_filtering()
        peaks.background_plot()
        peaks.filtering_negative()
        peaks.peak_searching(height=0, prominence=PROMINENCE, distance=6)
        print(peaks.peaks)
        peaks.state_plot()
        # for x in range(len(peaks.peaks)):
        peaks.custom_peak_fitting_with_parabole(0)
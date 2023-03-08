import pandas as pd

from processing.peak_classification import *
from processing.phase_classification import *
import os
import json
from datetime import date, datetime
import time

today = date.today()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'
current_session_results = ANALYSE_DIR_SESSIONS_RESULTS + str(today) + '/'

if not os.path.exists(current_session):
    os.mkdir(current_session)
if not os.path.exists(current_session_results):
    os.mkdir(current_session_results)


def get_filenames(folder_path):
    """
    Generator that yields the filenames in the given folder path.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            yield filename


def get_filenames_without_ext(folder_path):
    """
    Generator that yields the filenames (without extensions) in the given folder path.
    """
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # Split the filename into name and extension, and return just the name
            name, extension = os.path.splitext(filename)
            yield name


data = {}
files_number = 0
time_start = time.time()

get_breaked = True

for filename in get_filenames_without_ext(DATA_DIR):
    peaks = Peaks(filename, DATA_DIR, current_session)
    peaks.background_reduction()
    peaks.filtering()
    peaks.background_plot()
    peaks.filtering_negative()
    peaks.peak_processing()
    peaks.result_plot()
    data[peaks.file] = peaks.gathering()
    files_number += 1
    # print(peaks.peaks_data)
    if data[peaks.file]['peak_number'] == 0:
        continue

    phases = Fastdw(filename, current_session, defined_phases, class_names, data[peaks.file])
    phases.preset_plot()
    phases.data_preparing()
    phases.alignement()
    data[peaks.file] = phases.gathering()



time_final = time.time()
print('Taken: ', time_final - time_start)

with open(current_session_results + current_time + f'_{files_number}.json', 'w') as f:
    json.dump(data, f, indent=4, separators=(",", ": "))


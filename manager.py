from processing.peak_classification import *
# from processing.phase_classification import *
from datetime import date, datetime
import time

today = date.today()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

current_session = ANALYSE_DIR_SESSIONS + str(today) + '/'

class Manager:
    def __init__(self, current_session:str, DATA_DIR=DATA_DIR):
        self.DATA_DIR = DATA_DIR
        self.current_session = current_session
        self.data = {}

    def SingleProcessing(self, FILENAME):
        peaks = Peaks(FILENAME, self.DATA_DIR, current_session=self.current_session)
        peaks.background_reduction()
        peaks.filtering()
        peaks.background_plot()
        peaks.filtering_negative()
        peaks.peak_processing()
        peaks.result_plot()
        self.data = peaks.gathering()

    def print_data(self):
        print(self.data)




manager = Manager(current_session)
manager.SingleProcessing(FILENAME)
manager.print_data()


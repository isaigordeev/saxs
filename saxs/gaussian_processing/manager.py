import time
from typing import Any

from saxs.gaussian_processing.phase.phase_application import PhaseApplication
from saxs.gaussian_processing.peak.peak_application import PeakApplication
from .application import ApplicationManager

time_start1 = time.time()

import os

from datetime import datetime

time_start2 = time.time()

now = datetime.now()

today = now.today().date()

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


        if phase_data_directory is not None:
            self.phase_data_directory = phase_data_directory
        else:
            self.phase_data_directory = self._current_results_dir_session




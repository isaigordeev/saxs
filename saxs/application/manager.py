import time

from .application import ApplicationManager
from saxs.saxs.peak.abstract_kernel import AbstractPeakKernel
from saxs.saxs.peak.peak_application import PeakApplication
from saxs.saxs.phase.phase_application import PhaseApplication
from saxs.saxs.phase.phase_classificator import AbstractPhaseKernel

time_start1 = time.time()

import os
from datetime import datetime

time_start2 = time.time()

now = datetime.now()

today = now.today().date()


class Manager(ApplicationManager):
    def __init__(
        self,
        peak_data_path="test_processing_data/",
        phase_data_directory=None,
        peak_kernel: AbstractPeakKernel = None,
        phase_kernel: AbstractPhaseKernel = None,
        current_session=None,
    ) -> None:
        super().__init__(
            current_session=current_session,
            peak_kernel=peak_kernel,
            phase_kernel=phase_kernel,
        )

        self.peak_data_path = os.path.join(self.executing_path, peak_data_path)
        self.phase_data_directory = (
            self._default_peak_data_path
            if phase_data_directory is None
            else phase_data_directory
        )

    def __call__(self):
        if self.peak_classification:
            self.peak_application_instance = PeakApplication(
                self.peak_data_path, self.peak_kernel
            )
            self.peak_application_instance.peak_classification_run()

        if self.phase_classification:
            self.phase_application_instance = PhaseApplication(
                self.phase_data_directory, self.phase_kernel
            )
            self.phase_application_instance.phase_classification_run()

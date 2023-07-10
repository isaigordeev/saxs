import os
from abc import abstractmethod, ABC
from dataclasses import dataclass

from .settings_processing import ANALYSE_DIR, ANALYSE_DIR_SESSIONS_RESULTS, ANALYSE_DIR_SESSIONS


@dataclass
class AbstractProcessing(ABC):
    __slots__ = (
        'current_session',
        'current_date_session',
        'current_time',
    )

    def __init__(self, current_session):
        self.current_session = current_session
        current_date = str(current_session.today().date())

        self.current_date_session = "{}/".format(current_date)
        self.current_time = current_session.strftime("%H:%M:%S")


class Application(AbstractProcessing):
    def __init__(self, current_session, custom_output_directory=None):
        super().__init__(current_session)

        self.custom_output_directory = custom_output_directory
        self.executing_path = os.getcwd()

        self.analysis_dir = None
        self.analysis_dir_sessions = None
        self.results_dir_sessions = None
        self.current_results_dir_sessions = None

        self.set_directories()

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


@dataclass
class ApplicationClassificator(Application):
    __slots__ = ('data_directory',)

    def __init__(self, current_session, data_directory):
        super().__init__(current_session)

        self.data_directory = data_directory

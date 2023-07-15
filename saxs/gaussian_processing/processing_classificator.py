import os
from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime

from .settings_processing import ANALYSE_DIR, ANALYSE_DIR_SESSIONS_RESULTS, ANALYSE_DIR_SESSIONS


@dataclass
class AbstractApplication(ABC):
    current_root_session = datetime.now()
    executing_path = os.getcwd()

    __slots__ = (
        'current_session',
        'current_date_session',
        'current_time',
    )

    def __init__(self, current_session=None):
        if current_session is not None:
            self.current_session = current_session
        else:
            self.current_session = AbstractApplication.current_root_session

        current_date = str(self.current_session.today().date())

        self.current_date_session = "{}/".format(current_date)
        self.current_time = current_session.strftime("%H:%M:%S")


class Application(AbstractApplication):
    _analysis_dir = os.path.join(AbstractApplication.executing_path, ANALYSE_DIR)
    _analysis_dir_sessions = os.path.join(_analysis_dir, ANALYSE_DIR_SESSIONS)
    _results_dir_sessions = os.path.join(_analysis_dir, ANALYSE_DIR_SESSIONS_RESULTS)
    _current_results_dir_session = os.path.join(_results_dir_sessions,
                                                AbstractApplication.current_date_session)

    def __init__(self, current_session=None, custom_output_directory=None):
        super().__init__(current_session)

        self.custom_output_directory = custom_output_directory

        self.set_output_directories()

    def set_output_directories(self):

        if self.custom_output_directory is not None:
            Application._analysis_dir = os.path.join(self.custom_output_directory, ANALYSE_DIR)
            Application._analysis_dir_sessions = os.path.join(Application._analysis_dir, ANALYSE_DIR_SESSIONS)
            Application._results_dir_sessions = os.path.join(Application._analysis_dir, ANALYSE_DIR_SESSIONS_RESULTS)
            Application._current_results_dir_session = os.path.join(Application._results_dir_sessions,
                                                                    Application.current_date_session)

        if Application._analysis_dir is None:
            raise NotADirectoryError("Root output directory error")

        if not os.path.exists(Application._analysis_dir):
            os.mkdir(Application._analysis_dir)
        if not os.path.exists(Application._analysis_dir_sessions):
            os.mkdir(Application._analysis_dir_sessions)
        if not os.path.exists(Application._results_dir_sessions):
            os.mkdir(Application._results_dir_sessions)
        if not os.path.exists(Application._current_results_dir_session):
            os.mkdir(Application._current_results_dir_session)


@dataclass
class ApplicationClassificator(Application):
    # _data_directory = None

    def __init__(self, data_directory):
        assert data_directory is not None
        super().__init__(None, None)
        self.data_directory = data_directory


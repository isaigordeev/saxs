from abc import abstractmethod, ABC
from dataclasses import dataclass


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


@dataclass
class ProcessingClassificator(AbstractProcessing):
    __slots__ = ('data_directory',
                 'custom_directory',
                 )

    def __init__(self, current_session, data_directory, custom_output_directory=None):
        super().__init__(current_session)

        self.data_directory = data_directory
        self.current_session = current_session
        self.custom_directory = custom_output_directory

        current_date = str(current_session.today().date())
        self.current_date_session = "{}/".format(current_date)
        self.current_time = current_session.strftime("%H:%M:%S")







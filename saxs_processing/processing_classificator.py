from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class ProcessingClassificator(ABC):
    __slots__ = ('data_directory',
                 'custom_directory',
                 'current_session',
                 'current_data_session',
                 'current_time',
                 )

    def __init__(self, current_session, data_directory, custom_output_directory=None):

        self.data_directory = data_directory
        self.current_session = current_session
        self.custom_directory = custom_output_directory

        current_date = str(current_session.today().date())
        self.current_data_session = "{}/".format(current_date)
        self.current_time = current_session.strftime("%H:%M:%S")







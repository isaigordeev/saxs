from saxs_processing.abstr_phase import AbstractPhaseClassificator


class PhaseClassificator(AbstractPhaseClassificator):
    def __init__(self, data_directory, current_session):
        super().__init__(data_directory, current_session)
from scipy.optimize import curve_fit

from saxs.application.settings_processing import BACKGROUND_COEF
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.processing.functions import background_hyberbole


class BackgroundStage(AbstractStage):
    def __init__(self, _background_func=background_hyberbole):
        self.metadata = AbstractStageMetadata(
            data={
                "_background_func": _background_func,
                "_background_coef": BACKGROUND_COEF,
            }
        )

    def _process(self, stage_data):
        _background_func = self.metadata.get("_background_func")
        _background_coef = self.metadata.get("_background_coef")

        current_intensity_state = stage_data.get_intensity_array()
        current_q_state = stage_data.get_q_values_array()

        popt, pcov = curve_fit(
            f=_background_func,
            xdata=current_q_state,
            ydata=current_intensity_state,
            p0=(3, 2),
            sigma=stage_data.get_intensity_error_array(),
        )

        background = background_hyberbole(
            current_q_state,
            popt[0],
            popt[1],
        )

        current_intensity_state -= _background_coef * background

        return stage_data.set_intensity(current_intensity_state)

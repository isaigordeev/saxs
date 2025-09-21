from scipy.optimize import curve_fit

from saxs.application.settings_processing import BACKGROUND_COEF
from saxs.logging.logger import logger
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.processing.functions import background_hyberbole


class BackgroundStage(AbstractStage):
    def __init__(self, _background_func=background_hyberbole):
        self.metadata = AbstractStageMetadata(
            values={
                "_background_func": _background_func,
                "_background_coef": BACKGROUND_COEF,
            }
        )

    def _process(self, stage_data):
        _background_func = self.metadata.unwrap().get("_background_func")
        _background_coef = self.metadata.unwrap().get("_background_coef")

        q_vals = stage_data.get_q_values_array()
        intensity = stage_data.get_intensity_array()
        error = stage_data.get_intensity_error_array()

        # Log input state
        logger.info(
            f"\n=== BackgroundStage Input ===\n"
            f"Number of points: {len(q_vals)}\n"
            f"Q range:       [{min(q_vals)}, {max(q_vals)}]\n"
            f"Intensity:     [{min(intensity)}, {max(intensity)}]\n"
            f"Error:         [{min(error)}, {max(error)}]\n"
            f"============================="
        )

        # Fit background
        popt, pcov = curve_fit(
            f=_background_func,
            xdata=q_vals,
            ydata=intensity,
            p0=(3, 2),
            sigma=error,
        )

        # Log fitted parameters
        logger.info(
            f"\nFitted background parameters:\n"
            f"a = {popt[0]:.4f}, b = {popt[1]:.4f}"
        )

        # Subtract background
        background = _background_func(q_vals, *popt)
        intensity_subtracted = intensity - _background_coef * background

        # Log post-processing state
        logger.info(
            f"\n=== BackgroundStage Output ===\n"
            f"Background coefficient: {_background_coef}\n"
            f"Number of points:        {len(q_vals)}\n"
            f"Q range:                 [{min(q_vals)}, {max(q_vals)}]\n"
            f"Intensity range:         [{min(intensity_subtracted)}, {max(intensity_subtracted)}]\n"
            f"Background values:       [{min(background)}, {max(background)}]\n"
            f"============================="
        )

        return stage_data.set_intensity(intensity_subtracted), None

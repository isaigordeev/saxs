from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit

from saxs.application.settings_processing import BACKGROUND_COEF
from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.processing.functions import background_hyperbole
from saxs.saxs.processing.stage.background.types import (
    BackgroundStageMetadata,
    EBackMetadataKeys,
)


class BackgroundStage(IAbstractStage):
    def __init__(
        self,
        _background_func: Callable[
            ...,
            NDArray[np.float64],
        ] = background_hyperbole,
    ):
        self.metadata = BackgroundStageMetadata(
            value={
                EBackMetadataKeys.BACKGROUND_FUNC.value: _background_func,
                EBackMetadataKeys.BACKGROUND_COEF.value: BACKGROUND_COEF,
            },
        )

    def _process(self, sample: SAXSSample) -> SAXSSample:
        _background_func = self.metadata[EBackMetadataKeys.BACKGROUND_FUNC]
        _background_coef = self.metadata[EBackMetadataKeys.BACKGROUND_COEF]

        q_vals = sample[ESAXSSampleKeys.Q_VALUES]
        intensity = sample[ESAXSSampleKeys.INTENSITY]
        error = sample[ESAXSSampleKeys.INTENSITY_ERROR]

        # Log input state
        logger.info(
            f"\n=== BackgroundStage Input ===\n"
            f"Number of points: {len(q_vals)}\n"
            f"Q range:       [{min(q_vals)}, {max(q_vals)}]\n"
            f"Intensity:     [{min(intensity)}, {max(intensity)}]\n"
            f"Error:         [{min(error)}, {max(error)}]\n"
            f"=============================",
        )

        # Fit background
        popt, _pcov = curve_fit(
            f=_background_func,
            xdata=q_vals,
            ydata=intensity,
            p0=(3, 2),
            sigma=error,
        )

        # Log fitted parameters
        logger.info(
            f"\nFitted background parameters:\n"
            f"a = {popt[0]:.4f}, b = {popt[1]:.4f}",
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
            f"=============================",
        )

        return sample.set_intensity(intensity_subtracted), None

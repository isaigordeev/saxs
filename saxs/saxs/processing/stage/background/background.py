"""
Module: background.

This module defines the `BackgroundStage` class for SAXS data
processing. It provides functionality to fit and subtract a
background from intensity data using a user-defined or default
background function.

The module relies on `scipy.optimize.curve_fit` for fitting and
supports logging of intermediate and final processing states.
"""

from saxs.application.settings_processing import BACKGROUND_COEF
from saxs.logging.logger import get_stage_logger
from saxs.saxs.core.stage.abstract_stage import IAbstractStage

logger = get_stage_logger(__name__)
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.processing.functions import background_hyperbole
from saxs.saxs.processing.stage.background.types import (
    BackgroundStageMetadata,
    EBackMetadataKeys,
)
from saxs.saxs.processing.stage.common.fitting import Fitting

DEFAULT_BACKG_META = BackgroundStageMetadata(
    value={
        EBackMetadataKeys.BACKGROUND_FUNC.value: background_hyperbole,
        EBackMetadataKeys.BACKGROUND_COEF.value: BACKGROUND_COEF,
    },
)


class BackgroundStage(IAbstractStage[BackgroundStageMetadata]):
    """
    Stage to fit and subtract background from SAXS intensity data.

    This stage uses a callable background function to model the
    background and subtract it from the measured intensities.
    Metadata is stored to keep track of the background function
    and its associated coefficient.

    Parameters
    ----------
    _background_func : Callable[..., NDArray[np.float64]], optional
        Function to model the background. Defaults to
        `background_hyperbole`.

    Attributes
    ----------
    metadata : BackgroundStageMetadata
        Metadata storing the background function and coefficient.
    """

    def __init__(
        self,
        metadata: BackgroundStageMetadata | None,
    ):
        metadata = metadata or DEFAULT_BACKG_META

        super().__init__(metadata=metadata)

    def _process(self, sample: SAXSSample) -> SAXSSample:
        """
        Process a SAXS sample by fitting and subtracting background.

        Parameters
        ----------
        sample : SAXSSample
            SAXS sample containing q-values, intensity, intensity
            error, and metadata.

        Returns
        -------
        SAXSSample
            A new SAXS sample with the background-subtracted
            intensity.
        """
        _background_func = self.metadata[EBackMetadataKeys.BACKGROUND_FUNC]
        _background_coef = self.metadata[EBackMetadataKeys.BACKGROUND_COEF]

        q_vals = sample[ESAXSSampleKeys.Q_VALUES]
        intensity = sample[ESAXSSampleKeys.INTENSITY]
        error = sample[ESAXSSampleKeys.INTENSITY_ERROR]

        # Fit background
        popt, _ = Fitting.curve_fit(
            _background_func,
            q_vals,
            intensity,
            error,
            p0=(3.0, 2.0),
        )

        # Subtract background
        background = _background_func(q_vals, *popt)
        _subtracted_intensity = intensity - _background_coef * background

        # Log processing results
        logger.stage_info(
            "BackgroundStage",
            "Background fitted and subtracted",
            data_points=len(q_vals),
            q_range=f"[{min(q_vals):.4f}, {max(q_vals):.4f}]",
            fit_params=f"a={popt[0]:.4f}, b={popt[1]:.4f}",
            bg_coef=_background_coef,
            intensity_range=f"[{min(_subtracted_intensity):.4f}, {max(_subtracted_intensity):.4f}]",
        )

        sample[ESAXSSampleKeys.INTENSITY] = _subtracted_intensity

        return sample

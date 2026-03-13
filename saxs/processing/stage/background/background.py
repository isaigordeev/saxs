"""Background stage: fits and subtracts background from intensity."""

from saxs.logging.logger import get_stage_logger

from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.types.sample import SAXSSample
from saxs.processing.functions import background_hyperbole
from saxs.processing.stage.background.types import (
    BACKGROUND_COEF,
    BackgroundStageMetadata,
)
from saxs.processing.stage.common.fitting import Fitting

logger = get_stage_logger(__name__)

DEFAULT_BACKG_META = BackgroundStageMetadata(
    background_func=background_hyperbole,
    background_coef=BACKGROUND_COEF,
)


class BackgroundStage(IAbstractStage):
    """Fits and subtracts background from SAXS intensity data."""

    def __init__(self, metadata: BackgroundStageMetadata | None = None):
        super().__init__(metadata=metadata or DEFAULT_BACKG_META)

    def _process(self, sample: SAXSSample) -> SAXSSample:
        _background_func = self.metadata.background_func
        _background_coef = self.metadata.background_coef

        q_vals = sample.q_values
        intensity = sample.intensity
        error = sample.intensity_err

        logger.stage_info(
            "BackgroundStage",
            "Starting background fitting",
            data_points=len(q_vals),
            q_range=f"[{min(q_vals):.4f}, {max(q_vals):.4f}]",
            intensity_range=f"[{min(intensity):.4f}, {max(intensity):.4f}]",
        )

        logger.stage_info(
            "BackgroundStage",
            "Fitting hyperbolic function",
            function="I(q) = a/(q-b) + c",
        )

        popt, _ = Fitting.curve_fit(
            _background_func,
            q_vals,
            intensity,
            error,
            p0=(3.0, 2.0),
        )

        logger.stage_info(
            "BackgroundStage",
            "Fit successful",
            param_a=f"{popt[0]:.4f}",
            param_b=f"{popt[1]:.4f}",
        )

        background = _background_func(q_vals, *popt)
        _subtracted_intensity = intensity - _background_coef * background

        logger.stage_info(
            "BackgroundStage",
            "Background subtraction complete",
            bg_coefficient=_background_coef,
            bg_range=f"[{min(background):.4f}, {max(background):.4f}]",
            final_intensity=f"[{min(_subtracted_intensity):.4f}, {max(_subtracted_intensity):.4f}]",
        )

        sample.intensity = _subtracted_intensity

        return sample

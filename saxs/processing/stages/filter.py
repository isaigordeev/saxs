"""Filter stage: applies moving average smoothing."""

from saxs.logging.logger import get_stage_logger

from saxs.core.stage import IAbstractStage
from saxs.core.types import SAXSSample
from saxs.processing.functions import moving_average

logger = get_stage_logger(__name__)


class FilterStage(IAbstractStage):
    """Applies a moving average filter to intensity data."""

    def _process(self, sample: SAXSSample) -> SAXSSample:
        _intensity = sample.intensity

        logger.stage_info(
            "FilterStage",
            "Applying moving average filter",
            window_size=10,
            data_points=len(_intensity),
            intensity_range=f"[{min(_intensity):.4f}, {max(_intensity):.4f}]",
        )

        filtered_intensity = moving_average(_intensity, 10)
        sample.intensity = filtered_intensity

        logger.stage_info(
            "FilterStage",
            "Filtering complete",
            smoothed_range=f"[{min(filtered_intensity):.4f}, {max(filtered_intensity):.4f}]",
        )

        return sample

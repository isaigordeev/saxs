"""Filter Stage Module.

This module defines the `FilterStage` class, which implements a SAXS
data processing stage that applies a moving average filter to
intensity values within a `SAXSSample`.

Classes
-------
FilterStage
    Applies a moving average filter to intensity data.
"""

from saxs.logging.logger import get_stage_logger
from saxs.core.stage.abstract_stage import IAbstractStage

logger = get_stage_logger(__name__)
from saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.processing.functions import moving_average


class FilterStage(IAbstractStage):
    """Stage that applies a moving average filter to intensity data.

    This stage retrieves the intensity values from a `SAXSSample`,
    applies a moving average filter with a fixed window size, and
    updates the sample in place. The filtered intensity is stored
    under the `ESAXSSampleKeys.INTENSITY` key.

    The stage also logs the number of points processed.
    """

    def _process(self, sample: SAXSSample) -> SAXSSample:
        """Process a SAXSSample by applying a moving average filter.

        Parameters
        ----------
        sample : SAXSSample
            The SAXS sample containing q-values and intensity data.

        Returns
        -------
        SAXSSample
            The same sample object with filtered intensity values.

        Notes
        -----
        The filtering uses a fixed window size of 10 points.
        """
        _intensity = sample[ESAXSSampleKeys.INTENSITY]

        logger.stage_info(
            "FilterStage",
            "Applying moving average filter",
            window_size=10,
            data_points=len(_intensity),
            intensity_range=f"[{min(_intensity):.4f}, {max(_intensity):.4f}]",
        )

        filtered_intensity = moving_average(_intensity, 10)
        sample[ESAXSSampleKeys.INTENSITY] = filtered_intensity

        logger.stage_info(
            "FilterStage",
            "Filtering complete",
            smoothed_range=f"[{min(filtered_intensity):.4f}, {max(filtered_intensity):.4f}]",
        )

        return sample

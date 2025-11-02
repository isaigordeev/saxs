"""Filter Stage Module.

This module defines the `FilterStage` class, which implements a SAXS
data processing stage that applies a moving average filter to
intensity values within a `SAXSSample`.

Classes
-------
FilterStage
    Applies a moving average filter to intensity data.
"""

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.processing.functions import moving_average


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

        filtered_intensity = moving_average(_intensity, 10)
        sample[ESAXSSampleKeys.INTENSITY] = filtered_intensity

        logger.info(
            f"\n=== FilterStage Processing ===\n"
            f"Input points:     {len(sample[ESAXSSampleKeys.Q_VALUES])}\n"
            f"=============================",
        )

        return sample

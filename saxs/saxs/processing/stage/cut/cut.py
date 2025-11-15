"""
Module: saxs.processing.stage.filter.cut.cut_stage.

Defines the CutStage class for SAXS data preprocessing.

This module implements a data-processing stage that trims SAXS
sample arrays (q-values and intensity) starting from a specified
cut point. It is typically used as part of a SAXS data processing
pipeline, where only a subset of the scattering data beyond a
given q-index is retained.

Classes
-------
CutStage : AbstractStage
    A pipeline stage that slices q-values and intensity arrays
    according to the configured cut point.
"""

from saxs.logging.logger import get_stage_logger
from saxs.saxs.core.stage.abstract_stage import IAbstractStage

logger = get_stage_logger(__name__)
from saxs.saxs.core.types.sample import (
    ESAXSSampleKeys,
    SAXSSample,
)
from saxs.saxs.processing.stage.cut.types import (
    DEFAULT_CUT_POINT,
    CutStageMetadata,
    ECutStageMetadataKeys,
)

DEFAULT_CUT_META = CutStageMetadata(
    {
        ECutStageMetadataKeys.CUT_POINT.value: DEFAULT_CUT_POINT,
    },
)


class CutStage(IAbstractStage[CutStageMetadata]):
    """
    SAXS processing stage that trims data arrays.

    This stage takes a SAXS sample and removes all data points
    before the configured `cut_point`. It modifies the sample's
    q-values and intensity arrays accordingly and logs basic
    input/output statistics.

    Parameters
    ----------
    cut_point : int, optional
        Index at which to start slicing q-values and intensity
        arrays.
        Defaults to 100.

    Attributes
    ----------
    metadata : CutStageMetadata
        Metadata object holding the cut point configuration.

    Examples
    --------
    >>> stage = CutStage(cut_point=120)
    >>> new_sample, _ = stage._process(sample, flow_metadata)
    """

    def __init__(self, metadata: CutStageMetadata | None):
        metadata = metadata or DEFAULT_CUT_META

        super().__init__(metadata=metadata)

    def _process(
        self,
        sample: SAXSSample,
    ) -> "SAXSSample":
        metadata: CutStageMetadata = self.get_metadata()
        cut_point = metadata.get_cut_point()

        # Cut the data
        q_values_cut = sample[ESAXSSampleKeys.Q_VALUES][cut_point:]
        intensity_cut = sample[ESAXSSampleKeys.INTENSITY][cut_point:]
        error_cut = sample[ESAXSSampleKeys.INTENSITY_ERROR][cut_point:]

        # Assign
        # (implement err intensity)
        sample[ESAXSSampleKeys.Q_VALUES] = q_values_cut
        sample[ESAXSSampleKeys.INTENSITY] = intensity_cut
        sample[ESAXSSampleKeys.INTENSITY_ERROR] = error_cut

        # Log input/output info
        logger.stage_info(
            "CutStage",
            "Data truncated",
            cut_point=cut_point,
            output_points=len(q_values_cut),
            q_range=f"[{min(q_values_cut):.4f}, {max(q_values_cut):.4f}]",
            intensity_range=f"[{min(intensity_cut):.4f}, {max(intensity_cut):.4f}]",
        )

        return sample

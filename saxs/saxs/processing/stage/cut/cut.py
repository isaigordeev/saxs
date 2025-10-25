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

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.types.metadata import FlowMetadata
from saxs.saxs.core.types.sample import (
    SAXSSample,
    SAXSSampleKeys,
)
from saxs.saxs.processing.stage.cut.types import (
    CutStageMetadata,
    CutStageMetadataDictKeys,
)


class CutStage(AbstractStage):
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

    def __init__(self, cut_point: int = 100):
        self.metadata = CutStageMetadata(
            value={CutStageMetadataDictKeys.CUT_POINT.value: cut_point},
        )

    def _process(
        self,
        sample: SAXSSample,
        flow_metadata: FlowMetadata,
    ) -> tuple["SAXSSample", "FlowMetadata"]:
        cut_point = self.metadata.get_cut_point()

        # Cut the data
        q_values_cut = sample.get_q_values()[cut_point:]
        intensity_cut = sample.get_intensity()[cut_point:]

        # Assign
        # (implement err intensity)
        sample[SAXSSampleKeys.Q_VALUES] = q_values_cut
        sample[SAXSSampleKeys.INTENSITY] = q_values_cut

        # Log input/output info
        logger.info(
            f"\n=== CutStage Processing ===\n"
            f"Cut point:        {cut_point}\n"
            f"Input points:     {len(sample.get_q_values())}\n"
            f"Output points:    {len(q_values_cut)}\n"
            f"Q range (after):  [{min(q_values_cut)}, {max(q_values_cut)}]\n"
            f"Intensity range:  [{min(intensity_cut)}, {max(intensity_cut)}]\n"
            f"=============================",
        )

        return sample, flow_metadata

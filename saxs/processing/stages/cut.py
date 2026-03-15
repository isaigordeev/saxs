"""Cut stage: truncates SAXS data at a specified index."""

from dataclasses import dataclass

from saxs.logging.logger import get_stage_logger

from saxs.core.stage import IAbstractStage
from saxs.core.types import SAXSSample

logger = get_stage_logger(__name__)

DEFAULT_CUT_POINT = 100


@dataclass
class CutStageMetadata:
    """Configuration for the Cut stage."""

    cut_point: int = DEFAULT_CUT_POINT


DEFAULT_CUT_META = CutStageMetadata()


class CutStage(IAbstractStage):
    """Truncates q-values and intensity arrays from a cut point."""

    def __init__(self, metadata: CutStageMetadata | None = None):
        super().__init__(metadata=metadata or DEFAULT_CUT_META)

    def _process(self, sample: SAXSSample) -> SAXSSample:
        cut_point = self.metadata.cut_point

        original_size = len(sample.q_values)
        logger.stage_info(
            "CutStage",
            "Starting data truncation",
            input_points=original_size,
            cut_point=cut_point,
        )

        q_values_cut = sample.q_values[cut_point:]
        intensity_cut = sample.intensity[cut_point:]
        error_cut = sample.intensity_err[cut_point:]

        sample.q_values = q_values_cut
        sample.intensity = intensity_cut
        sample.intensity_err = error_cut

        logger.stage_info(
            "CutStage",
            "Truncation complete",
            removed_points=original_size - len(q_values_cut),
            remaining_points=len(q_values_cut),
            q_range=f"[{min(q_values_cut):.4f}, {max(q_values_cut):.4f}]",
            intensity_range=f"[{min(intensity_cut):.4f}, {max(intensity_cut):.4f}]",
        )

        return sample

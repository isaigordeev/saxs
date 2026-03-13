"""Peak finding stage.

Detects peaks in SAXS intensity data using scipy's find_peaks.
"""

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.signal import (  # pyright: ignore[reportMissingTypeStubs]
    find_peaks,  # pyright: ignore[reportUnknownVariableType]
)

from saxs.logging.logger import get_stage_logger

from saxs.core.stage.abstract_cond_stage import IAbstractRequestingStage
from saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.core.stage.request.abst_request import (
    IAbstractStageRequest,
    StageRequest,
)
from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample
from saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    PeakFindStageMetadata,
)

logger = get_stage_logger(__name__)


class FindPeakStage(IAbstractRequestingStage):
    """Detects peaks in SAXS intensity data."""

    def __init__(
        self,
        policy: SingleStageChainingPolicy,
        metadata: PeakFindStageMetadata = DEFAULT_PEAK_FIND_META,
    ):
        super().__init__(metadata, policy)

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        if not _sample.metadata.unprocessed_peaks:
            _sample.metadata.unprocessed_peaks = {}
        return _sample

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Pass unprocessed peaks from sample to flow metadata."""
        _flow_metadata.unprocessed_peaks = _sample.metadata.unprocessed_peaks
        return _flow_metadata

    def _process(self, sample: SAXSSample) -> SAXSSample:
        intensity = sample.intensity
        q_values = sample.q_values

        logger.stage_info(
            "FindPeakStage",
            "Starting peak detection",
            data_points=len(intensity),
            intensity_range=f"[{min(intensity):.2f}, {max(intensity):.2f}]",
        )

        peak_indices, properties = self._find_peaks(intensity)

        if len(peak_indices) > 0:
            peak_positions = [q_values[i] for i in peak_indices]
            peak_heights = [intensity[i] for i in peak_indices]
            logger.stage_info(
                "FindPeakStage",
                "Peaks detected",
                peaks_found=f"{len(peak_indices)}",
                peak_indices=f"{peak_indices}",
                peak_positions=f"q={[f'{p:.4f}' for p in peak_positions]}",
                peak_heights=f"I={[f'{h:.2f}' for h in peak_heights]}",
            )
        else:
            logger.stage_info("FindPeakStage", "No peaks detected")

        _peak_dict = {index: intensity[index] for index in peak_indices}
        sample.metadata.unprocessed_peaks = _peak_dict

        return sample

    def create_request(self, metadata: FlowMetadata) -> IAbstractStageRequest:
        """Create a request for peak processing."""
        _current_peaks = metadata.unprocessed_peaks

        # Pick the tallest peak
        _current_peak = (
            max(_current_peaks, key=lambda x: _current_peaks[x])
            if len(_current_peaks) > 0
            else None
        )

        if _current_peak is None:
            # No peaks found — create empty request to finish
            return StageRequest(
                condition_eval_metadata=FlowMetadata(current_peak=None),
                flow_metadata=FlowMetadata(),
            )

        _current_peaks.pop(_current_peak)
        logger.stage_info(
            "FindPeakStage",
            "Requesting peak processing",
            peak_index=f"Current peak {int(_current_peak)}",
            remaining_peaks=f"Remaining peaks len: {len(_current_peaks)}",
        )

        _current = {_current_peak: _current_peaks.get(_current_peak, np.float64(0.0))}

        metadata.current_peak = _current_peak

        eval_metadata = FlowMetadata(current_peak=_current_peak)

        return StageRequest(
            condition_eval_metadata=eval_metadata,
            flow_metadata=metadata,
        )

    def _find_peaks(
        self,
        intensity: NDArray[np.float64],
    ) -> tuple[list[int], dict[str, Any]]:
        """Find peaks using scipy."""
        peaks_indices, peaks_properties = find_peaks(  # type: ignore  # noqa: PGH003
            x=intensity,
            height=self.metadata.height,
            prominence=self.metadata.prominence,
            distance=self.metadata.distance,
        )
        return peaks_indices, peaks_properties  # pyright: ignore[reportUnknownVariableType]

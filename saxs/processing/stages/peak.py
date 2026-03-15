"""Peak detection and processing stages."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.signal import (  # pyright: ignore[reportMissingTypeStubs]
    find_peaks,  # pyright: ignore[reportUnknownVariableType]
)

from saxs.logging.logger import get_stage_logger

from saxs.core.stage import (
    IAbstractRequestingStage,
    IAbstractStageRequest,
    SingleStageChainingPolicy,
    StageRequest,
)
from saxs.core.types import FlowMetadata, SAXSSample
from saxs.processing.functions import gauss, parabole
from saxs.processing.stage.common.fitting import Fitting

logger = get_stage_logger(__name__)


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


@dataclass
class PeakFindStageMetadata:
    """Configuration for the FindPeak stage."""

    height: float = 0.5
    prominence: float = 0.3
    distance: int = 10


@dataclass
class ProcessPeakStageMetadata:
    """Configuration for the ProcessPeak stage."""

    fit_range: int = 2


DEFAULT_PEAK_FIND_META = PeakFindStageMetadata()
DEFAULT_PEAK_PROCESS_META = ProcessPeakStageMetadata()


# ---------------------------------------------------------------------------
# FindPeakStage
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# ProcessPeakStage
# ---------------------------------------------------------------------------


class ProcessPeakStage(IAbstractRequestingStage):
    """Fits and subtracts individual peaks using parabolic + Gaussian fits."""

    def __init__(
        self,
        policy: SingleStageChainingPolicy,
        metadata: ProcessPeakStageMetadata = DEFAULT_PEAK_PROCESS_META,
    ):
        super().__init__(metadata, policy)

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Transfer current peak index from flow metadata to sample."""
        _sample.metadata.current_peak = _flow_metadata.current_peak
        return _sample

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Mark current peak as processed."""
        _current = _flow_metadata.current_peak

        if _current is not None:
            _flow_metadata.processed_peaks[_current] = np.float64(0.0)

        _flow_metadata.current_peak = None
        _sample.metadata.current_peak = None

        return _flow_metadata

    def _process(self, sample: SAXSSample) -> SAXSSample:
        """Fit and subtract a peak using parabolic + Gaussian approach."""
        q_state = sample.q_values
        i_state = sample.intensity
        ierr_state = sample.intensity_err
        _current_peak_index = sample.metadata.current_peak

        if _current_peak_index is None:
            logger.stage_info(
                "ProcessPeakStage",
                "No valid peak to process",
            )
            return sample

        _fit_range: int = self.metadata.fit_range

        _delta_q = min(np.diff(q_state))
        _max_intensity = max(i_state)

        def _current_peak_parabole(
            x: NDArray[np.float64],
            sigma: float,
            ampl: float,
        ) -> NDArray[np.float64]:
            return parabole(
                x,
                mu=q_state[_current_peak_index],
                sigma=sigma,
                ampl=ampl,
            )

        def _current_peak_gauss(
            x: NDArray[np.float64],
            sigma: float,
            ampl: float,
        ) -> NDArray[np.float64]:
            return gauss(
                x,
                q_state[_current_peak_index],
                sigma,
                ampl,
            )

        logger.stage_info(
            "ProcessPeakStage",
            "Starting peak fitting",
            peak_index=_current_peak_index,
            peak_q=f"{q_state[_current_peak_index]:.4f}",
            peak_I=f"{i_state[_current_peak_index]:.2f}",
        )

        # --- First parabola fit ---
        left_range = max(_current_peak_index - _fit_range, 0)
        right_range = _current_peak_index + _fit_range

        logger.stage_info(
            "ProcessPeakStage",
            "Parabolic fit",
            window=f"[{left_range}:{right_range}]",
            points=right_range - left_range,
        )

        popt_parabola, _pcov = Fitting.curve_fit(
            _func=_current_peak_parabole,
            x_data=q_state[left_range:right_range],
            y_data=i_state[left_range:right_range],
            p0=None,
            bounds=([_delta_q**2, 1], [0.05, 4 * _max_intensity]),
            error=ierr_state[left_range:right_range],
        )

        gauss_range = int(popt_parabola[0] / _delta_q)

        logger.stage_info(
            "ProcessPeakStage",
            "Parabola OK",
            sigma=f"{popt_parabola[0]:.5f}",
            ampl=f"{popt_parabola[1]:.2f}",
        )

        # --- Refined Gaussian fit ---
        left_range = max(_current_peak_index - gauss_range, 0)
        right_range = min(_current_peak_index + gauss_range, len(i_state))

        logger.stage_info(
            "ProcessPeakStage",
            "Gaussian fit",
            window=f"[{left_range}:{right_range}]",
            points=right_range - left_range,
        )

        popt, _pcov = Fitting.curve_fit(
            _func=_current_peak_gauss,
            x_data=q_state[left_range:right_range],
            y_data=i_state[left_range:right_range],
            bounds=([_delta_q**2, 1], [0.05, 4 * _max_intensity]),
            p0=None,
            error=ierr_state[left_range:right_range],
        )

        logger.stage_info(
            "ProcessPeakStage",
            "Gaussian OK",
            sigma=f"{popt[0]:.5f}",
            ampl=f"{popt[1]:.2f}",
        )

        # Subtract Gaussian approximation
        _current_gauss_approximation = _current_peak_gauss(
            q_state, popt[0], popt[1],
        )

        new_intensity_state = i_state - _current_gauss_approximation
        new_intensity_state = np.maximum(new_intensity_state, 0)
        sample.intensity = new_intensity_state

        logger.stage_info(
            "ProcessPeakStage",
            "Peak subtracted",
            max_removed=f"{max(_current_gauss_approximation):.2f}",
            new_range=f"[{min(new_intensity_state):.2f}, {max(new_intensity_state):.2f}]",
        )

        return sample

    def create_request(self, metadata: FlowMetadata) -> StageRequest:
        """Request FindPeakStage to detect remaining peaks."""
        _current_peak = metadata.current_peak

        eval_metadata = FlowMetadata(current_peak=_current_peak)

        return StageRequest(
            condition_eval_metadata=eval_metadata,
            flow_metadata=metadata,
        )

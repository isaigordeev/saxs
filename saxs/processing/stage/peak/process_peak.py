"""Peak processing stage.

Fits and subtracts individual peaks from SAXS intensity data.
"""

import numpy as np
from numpy.typing import NDArray

from saxs.logging.logger import get_stage_logger

from saxs.core.stage.abstract_cond_stage import IAbstractRequestingStage
from saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.core.stage.request.abst_request import StageRequest
from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample
from saxs.processing.functions import gauss, parabole
from saxs.processing.stage.common.fitting import Fitting
from saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_PROCESS_META,
    ProcessPeakStageMetadata,
)

logger = get_stage_logger(__name__)


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

        # Reset current peak
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

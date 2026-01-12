"""Peak processing stage module.

This module implements the ProcessPeakStage, which processes
individual peaks detected in SAXS scattering data. The stage fits
peak profiles (using Gaussian or parabolic functions) and extracts
peak characteristics such as position, width, and amplitude.

The stage works in conjunction with FindPeakStage in an iterative
workflow, processing one peak at a time and updating flow metadata
to track processed and unprocessed peaks.

Classes
-------
ProcessPeakStage
    Stage implementation for processing individual peaks in data.
"""

# Created by Isai Gordeev on 20/09/2025.

import numpy as np
from numpy.typing import NDArray

from saxs.logging.logger import get_stage_logger
from saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.core.stage.request.abst_request import (
    EvalMetadata,
    StageRequest,
)
from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample
from saxs.core.types.sample_objects import (
    ESampleMetadataKeys,
)
from saxs.core.types.scheduler_metadata import (
    ERuntimeConstants,
)
from saxs.processing.functions import gauss, parabole
from saxs.processing.stage.common.fitting import Fitting
from saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_PROCESS_META,
    ProcessPeakStageMetadata,
)

logger = get_stage_logger(__name__)


class ProcessPeakStage(IAbstractRequestingStage[ProcessPeakStageMetadata]):
    """Processing stage for fitting and subtracting individual peaks.

    This stage processes a single peak in SAXS intensity data using a
    two-step fitting approach:
    1. Initial parabolic fit to estimate peak width
    2. Refined Gaussian fit for accurate peak characterization

    After fitting, the Gaussian approximation is subtracted from the
    intensity data, allowing subsequent iterations to detect and
    process remaining peaks.

    The stage works iteratively with FindPeakStage:
    - Receives peak index from flow metadata
    - Fits and subtracts the peak
    - Requests FindPeakStage to detect remaining peaks
    - Continues until no peaks remain

    Attributes
    ----------
    metadata : ProcessPeakStageMetadata
        Configuration parameters including fit range.
    policy : SingleStageChainingPolicy
        Policy controlling when to chain back to FindPeakStage.

    Notes
    -----
    The two-step fitting process:
    1. Parabolic fit provides initial sigma estimate
    2. Sigma determines Gaussian fit range
    3. Gaussian fit provides final peak characterization
    4. Gaussian subtracted from intensity data

    See Also
    --------
    FindPeakStage : Detects peaks in intensity data
    SingleStageChainingPolicy : Controls stage chaining behavior
    """

    def __init__(
        self,
        policy: SingleStageChainingPolicy,
        metadata: ProcessPeakStageMetadata = DEFAULT_PEAK_PROCESS_META,
    ):
        """Initialize the ProcessPeakStage.

        Parameters
        ----------
        policy : SingleStageChainingPolicy
            Chaining policy that controls conditional execution of
            FindPeakStage after peak processing.
        metadata : ProcessPeakStageMetadata, optional
            Stage configuration including fit range parameter.
            Defaults to DEFAULT_PEAK_PROCESS_META.
        """
        super().__init__(metadata, policy)

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Transfer current peak index from flow metadata to sample.

        Extracts the current peak index being processed from the flow
        metadata and stores it in the sample metadata for use during
        peak processing.

        Parameters
        ----------
        _sample : SAXSSample
            SAXS sample to be processed.
        _flow_metadata : FlowMetadata
            Flow metadata containing the current peak index.

        Returns
        -------
        SAXSSample
            Sample with updated metadata containing current peak index.
        """
        _current: int = _flow_metadata[FlowMetadata.Keys.CURRENT]
        _sample.set_metadata(ESampleMetadataKeys.CURRENT, _current)
        return _sample

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Update flow metadata after peak processing completion.

        Marks the current peak as processed by adding its index to the
        processed set, and resets the current peak indicator to signal
        that processing is complete.

        This method ensures proper state tracking for the iterative
        peak processing workflow.

        Parameters
        ----------
        _sample : SAXSSample
            SAXS sample that was just processed.
        _flow_metadata : FlowMetadata
            Flow metadata to be updated with processing results.

        Returns
        -------
        FlowMetadata
            Updated flow metadata with current peak marked as
            processed.
        """
        _current: int = _flow_metadata[FlowMetadata.Keys.CURRENT]

        if FlowMetadata.Keys.PROCESSED not in _flow_metadata:
            _flow_metadata[FlowMetadata.Keys.PROCESSED] = set()

        # delegate to scheduler the processed peak
        _processed = _flow_metadata[FlowMetadata.Keys.PROCESSED]
        _processed.add(_current)

        # change state of current peak
        _flow_metadata[FlowMetadata.Keys.CURRENT] = (
            ERuntimeConstants.PROCESSED_PEAK
        )

        _sample.set_metadata(
            ESampleMetadataKeys.CURRENT,
            ERuntimeConstants.PROCESSED_PEAK,
        )

        return _flow_metadata

    def _process(self, sample: SAXSSample) -> SAXSSample:
        """Process and subtract a peak from SAXS intensity arr.

        Implements a two-step fitting approach to accurately
        characterize and remove a peak:

        Step 1: Parabolic Fit
        - Fits a parabolic function around the peak using FIT_RANGE
        - Extracts initial sigma estimate
        - Uses sigma to determine optimal Gaussian fit range

        Step 2: Gaussian Fit
        - Refits with Gaussian function using improved range
        - Extracts final peak parameters (sigma, amplitude)
        - Subtracts Gaussian approximation from intensity

        The fitted Gaussian is subtracted from the intensity data,
        with negative values clipped to zero.

        Parameters
        ----------
        sample : SAXSSample
            SAXS sample containing q-values, intensity, and intensity
            error arrays. Must have CURRENT peak index in metadata.

        Returns
        -------
        SAXSSample
            Modified sample with peak subtracted from intensity data.

        Notes
        -----
        Fit bounds:
        - Sigma: [delta_q^2, 0.05]
        - Amplitude: [1, 4 * max_intensity]

        The method logs detailed fitting information at each step
        for debugging and analysis purposes.
        """
        q_state = sample[SAXSSample.Keys.Q_VALUES]
        i_state = sample[SAXSSample.Keys.INTENSITY]
        ierr_state = sample[SAXSSample.Keys.INTENSITY_ERROR]
        _current_peak_index: int = sample.get_metadata()[
            ESampleMetadataKeys.CURRENT
        ]

        # Check if peak index is valid (not an enum constant)
        if isinstance(_current_peak_index, ERuntimeConstants):
            logger.stage_info(
                "ProcessPeakStage",
                "No valid peak to process",
                peak_value=str(_current_peak_index),
            )
            return sample

        _fit_range: int = self.metadata[
            ProcessPeakStageMetadata.Keys.FIT_RANGE
        ]

        _delta_q = min(np.diff(q_state))
        _max_intensity = max(i_state)

        def _current_peak_parabole(
            x: NDArray[np.float64],
            sigma: float,
            ampl: float,
        ) -> NDArray[np.float64]:
            """Temporary parabole."""
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
            """Temporary gauss."""
            return gauss(
                x,
                q_state[_current_peak_index],
                sigma,
                ampl,
            )

        if _current_peak_index is not ERuntimeConstants:
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
            q_state,
            popt[0],
            popt[1],
        )

        new_intensity_state = i_state - _current_gauss_approximation
        new_intensity_state = np.maximum(new_intensity_state, 0)
        sample[SAXSSample.Keys.INTENSITY] = new_intensity_state

        logger.stage_info(
            "ProcessPeakStage",
            "Peak subtracted",
            max_removed=f"{max(_current_gauss_approximation):.2f}",
            new_range=f"[{min(new_intensity_state):.2f}, {max(new_intensity_state):.2f}]",
        )

        return sample

    def create_request(
        self,
        metadata: FlowMetadata,
    ) -> StageRequest:
        """Create a request to loop back to FindPeakStage.

        After processing a peak, this stage requests execution of
        FindPeakStage again to detect remaining peaks in the data.

        Parameters
        ----------
        metadata : FlowMetadata
            Flow metadata containing peak processing state.

        Returns
        -------
        StageRequest
            Request to execute FindPeakStage with updated metadata.
        """
        # Get current processed peak from metadata
        _current_peak = metadata[FlowMetadata.Keys.CURRENT]

        # Create evaluation metadata for policy condition
        eval_metadata = EvalMetadata(
            {FlowMetadata.Keys.CURRENT.value: _current_peak},
        )

        return StageRequest(
            condition_eval_metadata=eval_metadata,
            flow_metadata=metadata,
        )

# Created by Isai Gordeev on 20/09/2025.

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.flow_metadata import FlowMetadata
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import (
    ESampleMetadataKeys,
    SampleMetadata,
)
from saxs.saxs.core.types.scheduler_metadata import (
    ERuntimeConstants,
    SchedulerMetadata,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata
from saxs.saxs.processing.functions import gauss, parabole
from saxs.saxs.processing.stage.common.fitting import Fitting
from saxs.saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_PROCESS_META,
    ProcessPeakStageMetadata,
)


class ProcessPeakStage(IAbstractRequestingStage[ProcessPeakStageMetadata]):
    """Process peak stage."""

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
        _current: int = _flow_metadata[FlowMetadata.Keys.CURRENT]
        _sample.set_metadata(ESampleMetadataKeys.CURRENT, _current)
        return _sample

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Pass metadata from sample to flow metadata."""
        _current: int = _flow_metadata[FlowMetadata.Keys.CURRENT]

        _processed = _flow_metadata[FlowMetadata.Keys.PROCESSED]
        _processed.add(_current)

        _flow_metadata[FlowMetadata.Keys.CURRENT] = (
            ERuntimeConstants.PROCESSED_PEAK
        )

        _sample.set_metadata(
            ESampleMetadataKeys.CURRENT,
            ERuntimeConstants.PROCESSED_PEAK,
        )

        return _flow_metadata

    def _process(self, sample: SAXSSample) -> SAXSSample:
        q_state = sample[SAXSSample.Keys.Q_VALUES]
        i_state = sample[SAXSSample.Keys.INTENSITY]
        ierr_state = sample[SAXSSample.Keys.INTENSITY_ERROR]
        _current_peak_index: int = sample.get_metadata()[
            ESampleMetadataKeys.CURRENT
        ]

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

        # --- First parabola fit ---
        left_range = max(_current_peak_index - _fit_range, 0)
        right_range = min(_current_peak_index + _fit_range, len(q_state) - 1)

        logger.info(
            f"\n=== ProcessFitPeakStage: Initial Fit ===\n"
            f"Peak index: {_current_peak_index}\n"
            f"Fit range:  [{left_range}, {right_range}]\n"
            f"delta_q:    {_delta_q}\n"
            f"max_I:      {_max_intensity}\n"
            "=========================================\n",
        )

        left_range = max(_current_peak_index - _fit_range, 0)

        right_range = _current_peak_index + _fit_range

        logger.info(f"print left r {left_range}  {right_range}")

        popt, _pcov = Fitting.curve_fit(
            _func=_current_peak_parabole,
            x_data=q_state[left_range:right_range],
            y_data=i_state[left_range:right_range],
            p0=None,
            bounds=([_delta_q**2, 1], [0.05, 4 * _max_intensity]),
            error=ierr_state[left_range:right_range],
        )

        gauss_range = int(popt[0] / _delta_q)

        logger.info(
            f"\n--- First Fit Results ---\n"
            f"Sigma (σ):   {popt[0]:.5f}\n"  # noqa: RUF001
            f"Amplitude:   {popt[1]:.5f}\n"
            f"Gauss range: {gauss_range}\n",
        )

        logger.info(f"gauss_range {popt[0]} {gauss_range}")

        left_range = max(_current_peak_index - gauss_range, 0)

        right_range = min(_current_peak_index + gauss_range, len(i_state))

        popt, _pcov = Fitting.curve_fit(
            _func=_current_peak_gauss,
            x_data=q_state[left_range:right_range],
            y_data=i_state[left_range:right_range],
            bounds=([_delta_q**2, 1], [0.05, 4 * _max_intensity]),
            p0=None,
            error=ierr_state[left_range:right_range],
        )

        logger.info(
            "\n=== ProcessFitPeakStage: Refined Fit ===\n"
            f"Refined range: [{left_range}, {right_range}]\n"
            f"Refined σ:     {popt[0]:.5f}\n"
            f"Refined ampl:  {popt[1]:.5f}\n"
            f"=========================================\n",
        )

        _current_gauss_approximation = _current_peak_gauss(
            q_state,
            popt[0],
            popt[1],
        )

        new_intensity_state = i_state - _current_gauss_approximation

        new_intensity_state = np.maximum(new_intensity_state, 0)

        sample[SAXSSample.Keys.INTENSITY] = new_intensity_state

        logger.info(
            "\n+++ ProcessFitPeakStage Completed +++\n"
            f"Subtracted Gaussian approx (sigma={popt[0]:.5f}, A={popt[1]:.5f})\n"
            f"=====================================\n",
        )

        return sample

    def create_request(self):
        eval_metadata = TAbstractStageMetadata()
        pass_metadata = TAbstractStageMetadata()
        scheduler_metadata = SchedulerMetadata(self.metadata.unwrap())
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

# Created by Isai Gordeev on 20/09/2025.

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import ESampleMetadataKeys
from saxs.saxs.core.types.scheduler_metadata import SchedulerMetadata
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata
from saxs.saxs.processing.functions import gauss, parabole
from saxs.saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_PROCESS_META,
    ProcessPeakStageMetadata,
)


class ProcessPeakStage(IAbstractRequestingStage[ProcessPeakStageMetadata]):  # noqa: F821
    fit_range = 2

    def __init__(
        self,
        policy: SingleStageChainingPolicy,
        metadata: ProcessPeakStageMetadata = DEFAULT_PEAK_PROCESS_META,
    ):
        super().__init__(metadata, policy)

    def handle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Pass metadata from sample to flow metadata."""
        _flow_metadata[FlowMetadataKeys.UNPROCESSED] = _sample.get_metadata()[
            FlowMetadataKeys.UNPROCESSED
        ]

        return _flow_metadata

    def _process(self, sample: SAXSSample):
        q_state = sample[SAXSSample.Keys.Q_VALUES]
        _current_peak_index: int = sample.get_metadata()[
            ESampleMetadataKeys.CURRENT
        ]

        def _current_peak_parabole(
            x: NDArray[np.float64],
            sigma: float,
            ampl: float,
        ):
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
        ):
            return gauss(
                x,
                q_state[_current_peak_index],
                sigma,
                ampl,
            )

        # --- First parabola fit ---
        left_range = max(current_peak_index - self.fit_range, 0)
        right_range = current_peak_index + self.fit_range

        logger.info(
            "\n=== ProcessFitPeakStage: Initial Fit ===\n"
            f"Peak index: {current_peak_index}\n"
            f"Fit range:  [{left_range}, {right_range}]\n"
            f"delta_q:    {delta_q}\n"
            f"max_I:      {max_intensity}\n"
            "=========================================",
        )

        left_range = max(current_peak_index - self.fit_range, 0)

        right_range = current_peak_index + self.fit_range

        logger.info(f"print left r {left_range}  {right_range}")

        popt, pcov = curve_fit(
            f=_current_peak_parabole,
            xdata=current_q_state[left_range:right_range],
            ydata=current_intensity_state[left_range:right_range],
            bounds=([delta_q**2, 1], [0.05, 4 * max_intensity]),
            sigma=current_intensity_errors_state[left_range:right_range],
        )

        gauss_range = int(popt[0] / delta_q)

        logger.info(
            "\n--- First Fit Results ---\n"
            f"Sigma (σ):   {popt[0]:.5f}\n"  # noqa: RUF001
            f"Amplitude:   {popt[1]:.5f}\n"
            f"Gauss range: {gauss_range}\n"
            "--------------------------",
        )

        logger.info(f"gauss_range {popt[0]} {gauss_range}")

        left_range = max(current_peak_index - gauss_range, 0)

        right_range = current_peak_index + gauss_range

        popt, _pcov = curve_fit(
            f=_current_peak_gauss,
            xdata=current_q_state[left_range:right_range],
            ydata=current_intensity_state[left_range:right_range],
            bounds=([delta_q**2, 1], [0.05, 4 * max_intensity]),
            sigma=current_intensity_errors_state[left_range:right_range],
        )

        logger.info(
            "\n=== ProcessFitPeakStage: Refined Fit ===\n"
            f"Refined range: [{left_range}, {right_range}]\n"
            f"Refined σ:     {popt[0]:.5f}\n"
            f"Refined ampl:  {popt[1]:.5f}\n"
            "=========================================",
        )

        _current_gauss_approximation = _current_peak_gauss(
            current_q_state,
            popt[0],
            popt[1],
        )

        new_intensity_state = (
            current_intensity_state - _current_gauss_approximation
        )

        new_intensity_state = np.maximum(new_intensity_state, 0)

        new_sample_data = sample.set_intensity(new_intensity_state)

        logger.info(
            "\n+++ ProcessFitPeakStage Completed +++\n"
            f"Subtracted Gaussian approx (σ={popt[0]:.5f}, A={popt[1]:.5f})\n"
            "+++++++++++++++++++++++++++++++++++++",
        )

        return (
            new_sample_data,
            {
                "popt": [current_peak_index, popt[0], popt[1]],
                "current_peak_index": current_peak_index,
            },
        )

    def create_request(self):
        eval_metadata = TAbstractStageMetadata()
        pass_metadata = TAbstractStageMetadata()
        scheduler_metadata = SchedulerMetadata(self.metadata.unwrap())
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

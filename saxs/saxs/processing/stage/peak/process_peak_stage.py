# Created by Isai Gordeev on 20/09/2025.

from typing import TYPE_CHECKING

import numpy as np
from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.condition.constant_true_condition import (
    TrueCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.scheduler_metadata import AbstractSchedulerMetadata
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata
from saxs.saxs.processing.functions import gauss, parabole
from scipy.optimize import curve_fit

if TYPE_CHECKING:
    from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
        ChainingPolicy,
    )


class AProcessPeakStage(AbstractRequestingStage):
    def _process(self, sample_data):
        return sample_data, None


class ProcessFitPeakStage(AProcessPeakStage):
    fit_range = 2

    @classmethod
    def default_policy(cls) -> "ChainingPolicy":
        # This default policy will automatically inject NextStage if
        #  Condition is true
        from saxs.saxs.processing.stage.peak.find_peak_stage import (
            FindAllPeaksStage,
        )

        return SingleStageChainingPolicy(
            condition=TrueCondition(),
            pending_stages=FindAllPeaksStage,
        )

    def _process(self, sample_data: SAXSSample):
        current_peak_index = self.metadata.unwrap().get("current_peak_index")

        delta_q = sample_data.metadata.unwrap().get("delta_q")
        max_intensity = sample_data.metadata.unwrap().get("max_intensity")

        current_q_state = sample_data.get_q_values_array()
        current_intensity_state = sample_data.get_intensity_array()
        current_intensity_errors_state = (
            sample_data.get_intensity_error_array()
        )

        def current_peak_parabole(x, sigma, ampl):
            return parabole(
                x,
                current_q_state[current_peak_index],
                sigma,
                ampl,
            )

        def current_peak_gauss(x, sigma, ampl):
            return gauss(x, current_q_state[current_peak_index], sigma, ampl)

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
            f=current_peak_parabole,
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
            f=current_peak_gauss,
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

        _current_gauss_approximation = current_peak_gauss(
            current_q_state,
            popt[0],
            popt[1],
        )

        new_intensity_state = (
            current_intensity_state - _current_gauss_approximation
        )

        new_intensity_state = np.maximum(new_intensity_state, 0)

        new_sample_data = sample_data.set_intensity(new_intensity_state)

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
        scheduler_metadata = AbstractSchedulerMetadata(self.metadata.unwrap())
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

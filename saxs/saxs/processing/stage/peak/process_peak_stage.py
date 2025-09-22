#
# Created by Isai GORDEEV on 20/09/2025.
#

from scipy.optimize import curve_fit

from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.scheduler_objects import AbstractSchedulerMetadata
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.pipeline.condition.constant_true_condition import (
    TrueCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.processing.functions import gauss, parabole


class AProcessPeakStage(AbstractRequestingStage):
    def _process(self, sample_data):
        return sample_data, None


class ProcessFitPeakStage(AProcessPeakStage):
    fit_range = 2

    @classmethod
    def default_policy(cls) -> "ChainingPolicy":
        # This default policy will automatically inject NextStage if Condition is true
        from saxs.saxs.processing.stage.peak.find_peak_stage import (
            FindAllPeaksStage,
        )

        return SingleStageChainingPolicy(
            condition=TrueCondition(),
            next_stage_cls=FindAllPeaksStage,
        )

    def _process(self, sample_data: SAXSSample):
        current_peak_index = self.metadata.unwrap().get("current_peak_index")

        delta_q = sample_data.metadata.unwrap().get("delta_q")
        max_intensity = sample_data.metadata.unwrap().get("max_intensity")

        current_q_state = sample_data.get_q_values_array()
        current_intensity_state = sample_data.get_intensity_array()
        current_intensity_errors_state = sample_data.get_intensity_error_array()

        def current_peak_parabole(x, sigma, ampl):
            return parabole(x, current_q_state[current_peak_index], sigma, ampl)

        def current_peak_gauss(x, sigma, ampl):
            return gauss(x, current_peak_index, sigma, ampl)

        left_range = (
            current_peak_index - self.fit_range
            if current_peak_index - self.fit_range >= 0
            else 0
        )

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

        left_range = (
            current_peak_index - gauss_range
            if current_peak_index - gauss_range
            else 0
        )

        right_range = current_peak_index + gauss_range

        popt, pcov = curve_fit(
            f=current_peak_parabole,
            xdata=current_q_state[left_range:right_range],
            ydata=current_intensity_state[left_range:right_range],
            bounds=([self.delta_q**2, 1], [0.05, 4 * self.max_I]),
            sigma=current_intensity_errors_state[left_range:right_range],
        )

        _current_gauss_approximation = current_peak_gauss(
            self.current_q_state, popt[0], popt[1]
        )

        new_intensity_state = (
            current_intensity_state - _current_gauss_approximation
        )

        new_sample_data = sample_data.set_intensity(new_intensity_state)

        return (
            new_sample_data,
            {"popt": [current_peak_index, popt[0], popt[1]]},
        )

    def create_request(self):
        eval_metadata = AbstractStageMetadata()
        pass_metadata = AbstractStageMetadata()
        scheduler_metadata = AbstractSchedulerMetadata(self.metadata.unwrap())
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

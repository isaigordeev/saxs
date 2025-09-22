#
# Created by Isai GORDEEV on 20/09/2025.
#

from typing import Optional, Type

from scipy.signal import find_peaks

from saxs.logging.logger import logger
from saxs.saxs.core.data.scheduler_objects import AbstractSchedulerMetadata
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractConditionalStage,
    AbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest


class FindAllPeaksStage(AbstractRequestingStage):
    def __init__(
        self, metadata, policy: Optional[SingleStageChainingPolicy] = None
    ):
        super().__init__(metadata, policy)

    @classmethod
    def default_policy(cls) -> "ChainingPolicy":
        # This default policy will automatically inject NextStage if Condition is true
        from saxs.saxs.processing.stage.peak.process_peak_stage import (
            ProcessFitPeakStage,
        )

        return SingleStageChainingPolicy(
            condition=ChainingPeakCondition("peaks"),
            next_stage_cls=ProcessFitPeakStage,
        )

    def _process(self, sample_data):
        intensity = sample_data.get_intensity_array()

        # Find peaks
        peaks_indices, peaks_properties = find_peaks(
            intensity,
            height=0.5,
            prominence=0.3,
            distance=10,
        )

        # Log peaks info in readable format
        logger.info(
            f"\n=== FindAllPeaksStage ===\n"
            f"Number of points:      {len(intensity)}\n"
            f"Number of peaks found: {len(peaks_indices)}\n"
            f"Peaks indices:         {list(peaks_indices)}\n"
            f"Intensity range:       [{min(intensity)}, {max(intensity)}]\n"
            f"==========================="
        )

        return sample_data, {"peaks": peaks_indices}

    def create_request(self) -> StageRequest:
        eval_metadata = self.metadata
        pass_metadata = AbstractStageMetadata(
            {"current_peak_index": (self.metadata.unwrap().get("peaks")[0])}
        )  # first peak
        scheduler_metadata = AbstractSchedulerMetadata(self.metadata.unwrap())
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

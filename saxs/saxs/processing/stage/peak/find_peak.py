# Created by Isai Gordeev on 20/09/2025.

from typing import TYPE_CHECKING

from scipy.signal import (  # pyright: ignore[reportMissingTypeStubs]
    find_peaks,  # # pyright: ignore[reportUnknownVariableType]
)

from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.saxs.core.stage.abstract_stage import TStageMetadata
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.core.types.scheduler_metadata import AbstractSchedulerMetadata
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata
from saxs.saxs.processing.stage.peak.types import (
    PeakFindStageMetadata,
    PeakProcessStageMetadata,
)

if TYPE_CHECKING:
    from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
        ChainingPolicy,
    )


class FindPeakStage(IAbstractRequestingStage[PeakFindStageMetadata]):
    def __init__(
        self,
        metadata: PeakFindStageMetadata,
        policy: SingleStageChainingPolicy[PeakFindStageMetadata],
    ):
        super().__init__(metadata, policy)

    @classmethod
    def default_policy(cls) -> "ChainingPolicy":
        from saxs.saxs.processing.stage.peak.process_peak_stage import (  # noqa: PLC0415
            ProcessFitPeakStage,
        )

        return SingleStageChainingPolicy(
            condition=ChainingPeakCondition("peaks"),
            pending_stages=ProcessFitPeakStage,
        )

    def _process(self, sample: SAXSSample) -> SAXSSample:
        intensity = sample[ESAXSSampleKeys.INTENSITY]

        # Find peaks
        peaks_indices, _peaks_properties = find_peaks(
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
            f"===========================",
        )

        return sample, {"peaks": peaks_indices}

    def create_request(self) -> StageRequest:
        _current_peak_index = (
            self.metadata.unwrap().get("peaks")[0]
            if len(self.metadata.unwrap().get("peaks")) > 0
            else -1
        )

        if _current_peak_index == -1:
            return None

        pass_metadata = TAbstractStageMetadata(
            {"current_peak_index": (_current_peak_index)},
        )  # first peak
        eval_metadata = self.metadata
        scheduler_metadata = AbstractSchedulerMetadata()
        return StageRequest(eval_metadata, pass_metadata, scheduler_metadata)

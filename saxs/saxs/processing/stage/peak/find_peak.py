# Created by Isai Gordeev on 20/09/2025.

from typing import TYPE_CHECKING, Any

import numpy as np
from numpy.typing import NDArray
from scipy.signal import (  # pyright: ignore[reportMissingTypeStubs]
    find_peaks,  # # pyright: ignore[reportUnknownVariableType]
)

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import StageRequest
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.core.types.scheduler_metadata import AbstractSchedulerMetadata
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata
from saxs.saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    EPeakFindMetadataKeys,
    PeakFindStageMetadata,
)


class FindPeakStage(IAbstractRequestingStage[PeakFindStageMetadata]):
    def __init__(
        self,
        policy: SingleStageChainingPolicy[PeakFindStageMetadata],
        metadata: PeakFindStageMetadata = DEFAULT_PEAK_FIND_META,
    ):
        super().__init__(metadata, policy)

    def _process(self, sample: SAXSSample) -> SAXSSample:
        intensity = sample[ESAXSSampleKeys.INTENSITY]

        # Find peaks
        peak_indices, peak_properties = self.find_peaks(intensity)

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
            self.metadata
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

    def find_peaks(self, intensity: NDArray[np.float64]):
        peaks_indices, peaks_properties = find_peaks(
            x=intensity,
            height=self.metadata[EPeakFindMetadataKeys.HEIGHT],
            prominence=self.metadata[EPeakFindMetadataKeys.PROMINENCE],
            distance=self.metadata[EPeakFindMetadataKeys.DISTANCE],
        )

        return peaks_indices, peaks_properties

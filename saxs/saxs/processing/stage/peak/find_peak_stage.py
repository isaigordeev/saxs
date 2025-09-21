#
# Created by Isai GORDEEV on 20/09/2025.
#

from typing import Type
from scipy.signal import find_peaks

from saxs.logging.logger import logger
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import AbstractConditionalStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    AProcessPeakStage,
)


class FindAllPeaksStage(AbstractConditionalStage):
    def __init__(
        self,
        chaining_stage: Type[AProcessPeakStage] = AProcessPeakStage,
        condition: SampleCondition = ChainingPeakCondition("dummy_key"),
    ):
        super().__init__(chaining_stage, condition)

    def _process(self, stage_data):
        intensity = stage_data.get_intensity_array()

        # Find peaks
        peaks_indices, peaks_properties = find_peaks(intensity)

        processed_stage_data = stage_data.set_metadata_dict(
            {"peaks": peaks_indices}
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

        return processed_stage_data, {"peaks": peaks_indices}

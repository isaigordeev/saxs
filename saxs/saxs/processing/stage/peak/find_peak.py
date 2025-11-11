# Created by Isai Gordeev on 20/09/2025.

from typing import Any

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
from saxs.saxs.core.stage.request.abst_request import (
    AbstractStageRequest,
    EvalMetadata,
    StageRequest,
)
from saxs.saxs.core.types.flow_metadata import (
    FlowMetadata,
    FlowMetadataKeys,
)
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.core.types.scheduler_metadata import SchedulerMetadata
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

    def handle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        _flow_metadata[FlowMetadataKeys.UNPROCESSED] = _sample

    def _process(
        self,
        sample: SAXSSample,
    ) -> SAXSSample:
        intensity = sample[ESAXSSampleKeys.INTENSITY]

        # Find peaks
        peak_indices, _ = self.find_peaks(intensity)

        # Log peaks info in readable format
        logger.info(
            f"\n=== FindAllPeaksStage ===\n"
            f"Number of points:      {len(intensity)}\n"
            f"Number of peaks found: {len(peak_indices)}\n"
            f"Peaks indices:         {list(peak_indices)}\n"
            f"Intensity range:       [{min(intensity)}, {max(intensity)}]\n"
            f"===========================",
        )

        return sample

    def create_request(self, metadata: FlowMetadata) -> AbstractStageRequest:
        eval_metadata = EvalMetadata(
            {
                FlowMetadataKeys.UNPROCESSED.value: metadata[
                    FlowMetadataKeys.UNPROCESSED
                ],
            },
        )

        scheduler_metadata = SchedulerMetadata({})

        return StageRequest(
            condition_eval_metadata=eval_metadata,
            scheduler_metadata=scheduler_metadata,
            flow_metadata=metadata,
        )

    def find_peaks(
        self,
        intensity: NDArray[np.float64],
    ) -> tuple[list[int], dict[str, Any]]:
        """Find peak func."""
        peaks_indices, peaks_properties = find_peaks(  # type: ignore  # noqa: PGH003
            x=intensity,
            height=self.metadata[EPeakFindMetadataKeys.HEIGHT],
            prominence=self.metadata[EPeakFindMetadataKeys.PROMINENCE],
            distance=self.metadata[EPeakFindMetadataKeys.DISTANCE],
        )

        return peaks_indices, peaks_properties  # pyright: ignore[reportUnknownVariableType]

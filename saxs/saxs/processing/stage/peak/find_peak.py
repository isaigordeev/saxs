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
from saxs.saxs.core.types.sample_objects import ESampleMetadataKeys
from saxs.saxs.core.types.scheduler_metadata import (
    ERuntimeConstants,
    SchedulerMetadata,
)
from saxs.saxs.processing.stage.peak.types import (
    DEFAULT_PEAK_FIND_META,
    EPeakFindMetadataKeys,
    PeakFindStageMetadata,
)


class FindPeakStage(IAbstractRequestingStage[PeakFindStageMetadata]):
    """Find peak stage."""

    def __init__(
        self,
        policy: SingleStageChainingPolicy,
        metadata: PeakFindStageMetadata = DEFAULT_PEAK_FIND_META,
    ):
        super().__init__(metadata, policy)

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        _metadata = _sample.get_metadata()

        if ESampleMetadataKeys.PROCESSED not in _metadata:
            _sample.set_metadata(ESampleMetadataKeys.PROCESSED, set())

        if ESampleMetadataKeys.UNPROCESSED not in _metadata:
            _sample.set_metadata(ESampleMetadataKeys.UNPROCESSED, set())

        return _sample

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Pass metadata from sample to flow metadata."""
        _flow_metadata[FlowMetadataKeys.UNPROCESSED] = _sample.get_metadata()[
            FlowMetadataKeys.UNPROCESSED
        ]

        _flow_metadata[FlowMetadataKeys.PROCESSED] = _sample.get_metadata()[
            FlowMetadataKeys.PROCESSED
        ]

        return _flow_metadata

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
            f"===========================\n",
        )

        sample.set_metadata(ESampleMetadataKeys.UNPROCESSED, set(peak_indices))

        return sample

    def create_request(self, metadata: FlowMetadata) -> AbstractStageRequest:
        """Create a request for peak processing."""
        _current_peaks: set[np.int64] = metadata[FlowMetadataKeys.UNPROCESSED]

        _current_peak = (
            _current_peaks.pop()
            if len(_current_peaks) > 0
            else ERuntimeConstants.UNDEFINED_PEAK
        )  # more flexible peak choice

        metadata[FlowMetadata.Keys.CURRENT] = _current_peak

        eval_metadata = EvalMetadata(
            {FlowMetadataKeys.CURRENT.value: _current_peak},
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

"""Peak finding stage module.

This module implements the FindPeakStage, which detects peaks in SAXS
scattering data using scipy's find_peaks algorithm. The stage processes
intensity data and identifies peak positions based on configurable
parameters such as height, prominence, and distance.

The stage uses a chaining policy to conditionally request the
ProcessPeakStage when peaks are detected, enabling iterative peak
processing workflows.

Classes
-------
FindPeakStage
    Stage implementation for detecting peaks in SAXS intensity data.
"""

# Created by Isai Gordeev on 20/09/2025.

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.signal import (  # pyright: ignore[reportMissingTypeStubs]
    find_peaks,  # # pyright: ignore[reportUnknownVariableType]
)

from saxs.logging.logger import get_stage_logger

logger = get_stage_logger(__name__)
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
        q_values = sample[ESAXSSampleKeys.Q_VALUES]

        logger.stage_info(
            "FindPeakStage",
            "Starting peak detection",
            data_points=len(intensity),
            intensity_range=f"[{min(intensity):.2f}, {max(intensity):.2f}]",
        )

        # Find peaks
        peak_indices, properties = self.find_peaks(intensity)

        if len(peak_indices) > 0:
            peak_positions = [q_values[i] for i in peak_indices]
            peak_heights = [intensity[i] for i in peak_indices]
            logger.stage_info(
                "FindPeakStage",
                "Peaks detected",
                peaks_found=len(peak_indices),
                peak_indices=str(peak_indices),
                peak_positions=f"q={[f'{p:.4f}' for p in peak_positions[:3]]}{'...' if len(peak_positions) > 3 else ''}",
                peak_heights=f"I={[f'{h:.2f}' for h in peak_heights[:3]]}{'...' if len(peak_heights) > 3 else ''}",
            )
        else:
            logger.stage_info(
                "FindPeakStage",
                "No peaks detected",
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

        if _current_peak != ERuntimeConstants.UNDEFINED_PEAK:
            logger.stage_info(
                "FindPeakStage",
                "Requesting peak processing",
                peak_index=int(_current_peak),
                remaining_peaks=len(_current_peaks),
            )

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

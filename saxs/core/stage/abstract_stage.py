"""Abstract base class for pipeline stages."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from saxs.core.types.flow_metadata import FlowMetadata
from saxs.core.types.sample import SAXSSample

if TYPE_CHECKING:
    from saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class IAbstractStage(ABC):
    """Base class for a processing stage in a SAXS data pipeline.

    Attributes
    ----------
    metadata : Any
        Stage-specific configuration metadata.
    """

    def __init__(self, metadata: Any = None):
        self.metadata = metadata

    def process(
        self,
        sample: SAXSSample,
        flow_metadata: FlowMetadata,
    ) -> tuple[SAXSSample, FlowMetadata]:
        """Process sample data with metadata hooks."""
        _sample = self._prehandle_flow_metadata(sample, flow_metadata)
        _sample = self._process(_sample)
        _flow_metadata = self._posthandle_flow_metadata(_sample, flow_metadata)
        return _sample, _flow_metadata

    @abstractmethod
    def _process(self, sample: SAXSSample) -> SAXSSample:
        """Implement stage-specific processing logic."""
        raise NotImplementedError

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Hook for updating flow metadata after processing."""
        _ = _sample
        return _flow_metadata

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Hook for updating sample from flow metadata before processing."""
        _ = _flow_metadata
        return _sample

    def request_stage(
        self,
        metadata: FlowMetadata,
    ) -> list["StageApprovalRequest"]:
        """Optionally request additional stages based on flow metadata."""
        _ = metadata
        return []

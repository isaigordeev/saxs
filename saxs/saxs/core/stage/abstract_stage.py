"""
Module: abstract_stage.

Defines the AbstractStage base class for SAXS data processing
pipelines.

This module provides an abstract interface for pipeline stages that
process SAXSSample objects and manage associated FlowMetadata. It
handles common metadata management, while requiring subclasses to
implement the actual processing logic in `_process`.

Classes:
    AbstractStage: Base class for all pipeline stages with metadata
    support.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from saxs.saxs.core.types.flow_metadata import FlowMetadata
from saxs.saxs.core.types.metadata import TMetadataSchemaDict
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


TStageMetadata = TypeVar(
    "TStageMetadata",
    bound=TAbstractStageMetadata[Any],  # kind of bottleneck in templates
)


class IAbstractStage(ABC, Generic[TStageMetadata]):
    """
    Base class for a processing stage in a SAXS data pipeline.

    Stages are responsible for processing SAXSSample objects and
    updating FlowMetadata. Provides hooks for metadata handling and
    enforces a `_process` method for subclasses to implement the
    actual processing logic.

    Attributes
    ----------
        metadata (AbstractStageMetadata): Metadata specific to this
        stage.
    """

    def __init__(
        self,
        metadata: TAbstractStageMetadata[TMetadataSchemaDict] | None = None,
    ):
        """
        Initialize the stage with optional metadata.

        Args:
            metadata (AbstractStageMetadata | None): Metadata for
            this stage.
                If None, an empty AbstractStageMetadata object is
                created.
        """
        self.metadata = (
            metadata if metadata else TAbstractStageMetadata(value={})
        )

    def process(
        self,
        sample: SAXSSample,
        flow_metadata: FlowMetadata,
    ) -> tuple["SAXSSample", "FlowMetadata"]:
        """
        Public method to process sample data with metadata.

        Handles the overall processing workflow:
        1. Calls the stage-specific `_process` method.
        2. Delegates metadata updates to `handle_metadata`.

        Args:
            sample_data (SAXSSample): The SAXS sample to process.
            metadata (FlowMetadata): Associated flow metadata.

        Returns
        -------
            tuple[SAXSSample, FlowMetadata]: Processed sample and
            updated metadata.
        """
        _sample = self._process(sample)

        # Delegate flow metadata management to hook
        _flow_metadata = self.handle_flow_metadata(_sample, flow_metadata)

        return _sample, _flow_metadata

    @abstractmethod
    def _process(
        self,
        sample: SAXSSample,
    ) -> "SAXSSample":
        """
        Abstract method to implement the processing logic.

        Subclasses must override this method to perform
        stage-specific processing.

        Args:
            sample_data (SAXSSample): The SAXS sample to process.
            metadata (FlowMetadata): Metadata associated with the
            sample.

        Returns
        -------
            tuple[SAXSSample, FlowMetadata]: Updated sample and
            metadata.
        """
        raise NotImplementedError

    def handle_flow_metadata(
        self,
        _sample: "SAXSSample",
        _flow_metadata: "FlowMetadata",
    ) -> "FlowMetadata":
        """Manage metadata updates after processing.

        Default behavior: does nothing with metadata and returns
        the sample. Can be overridden in subclasses to create
        a metadata request for scheduler or future samples.

        Args:
            _sample (SAXSSample): Processed sample data.
            _metadata (FlowMetadata): Metadata associated with the
            sample.

        Returns
        -------
            FlowMetadata: Flowmetadata data, potentially updated.
        """
        _ = _sample
        return _flow_metadata

    def request_stage(self) -> list["StageApprovalRequest"]:
        """
        Optionally requests dependencies or other stages.

        Returns
        -------
            list: Empty list by default. Override in subclasses if
            needed.
        """
        return []

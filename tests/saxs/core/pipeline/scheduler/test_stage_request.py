#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for stage_request.py module.
"""

import pytest
from dataclasses import FrozenInstanceError

from saxs.saxs.core.pipeline.scheduler.stage_request import (
    AbstractStageRequest,
    StageRequest,
)
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage


class TestAbstractStageRequest:
    """Test cases for AbstractStageRequest class."""

    def test_abstract_stage_request_creation(self):
        """Test creating AbstractStageRequest."""
        request = AbstractStageRequest()
        assert isinstance(request, AbstractStageRequest)

    def test_abstract_stage_request_immutable(self):
        """Test that AbstractStageRequest is immutable."""
        request = AbstractStageRequest()

        # Should not be able to modify attributes
        with pytest.raises(FrozenInstanceError):
            request.some_attribute = "value"

    def test_abstract_stage_request_equality(self):
        """Test AbstractStageRequest equality comparison."""
        request1 = AbstractStageRequest()
        request2 = AbstractStageRequest()

        # Empty requests should be equal
        assert request1 == request2

    def test_abstract_stage_request_hash(self):
        """Test AbstractStageRequest hashability."""
        request = AbstractStageRequest()

        # Should be hashable (can be used as dict key)
        request_dict = {request: "test_value"}
        assert request_dict[request] == "test_value"


class TestStageRequest:
    """Test cases for StageRequest class."""

    def test_stage_request_creation(self, mock_stage, stage_metadata):
        """Test creating StageRequest with stage and metadata."""
        request = StageRequest(stage=mock_stage, metadata=stage_metadata)

        assert request.stage == mock_stage
        assert request.metadata == stage_metadata

    def test_stage_request_creation_with_none_values(self):
        """Test creating StageRequest with None values."""
        request = StageRequest(stage=None, metadata=None)

        assert request.stage is None
        assert request.metadata is None

    def test_stage_request_immutable(self, mock_stage, stage_metadata):
        """Test that StageRequest is immutable."""
        request = StageRequest(stage=mock_stage, metadata=stage_metadata)

        # Should not be able to modify attributes
        with pytest.raises(FrozenInstanceError):
            request.stage = None

        with pytest.raises(FrozenInstanceError):
            request.metadata = None

    def test_stage_request_equality(self, mock_stage, stage_metadata):
        """Test StageRequest equality comparison."""
        request1 = StageRequest(stage=mock_stage, metadata=stage_metadata)
        request2 = StageRequest(stage=mock_stage, metadata=stage_metadata)

        # Same stage and metadata should be equal
        assert request1 == request2

        # Different metadata should not be equal
        different_metadata = AbstractStageMetadata({"different": "value"})
        request3 = StageRequest(stage=mock_stage, metadata=different_metadata)
        assert request1 != request3

    def test_stage_request_hash(self, mock_stage, stage_metadata):
        """Test StageRequest hashability."""
        request = StageRequest(stage=mock_stage, metadata=stage_metadata)

        # Should be hashable (can be used as dict key)
        request_dict = {request: "test_value"}
        assert request_dict[request] == "test_value"

    def test_stage_request_with_different_stage_types(self, stage_metadata):
        """Test StageRequest with different stage types."""

        # Create different mock stages
        class MockStage1(AbstractStage):
            def _process(self, stage_data):
                return stage_data

        class MockStage2(AbstractStage):
            def _process(self, stage_data):
                return stage_data

        stage1 = MockStage1()
        stage2 = MockStage2()

        request1 = StageRequest(stage=stage1, metadata=stage_metadata)
        request2 = StageRequest(stage=stage2, metadata=stage_metadata)

        # Different stage types should not be equal
        assert request1 != request2

    def test_stage_request_with_different_metadata(self, mock_stage):
        """Test StageRequest with different metadata."""
        metadata1 = AbstractStageMetadata({"key1": "value1"})
        metadata2 = AbstractStageMetadata({"key2": "value2"})

        request1 = StageRequest(stage=mock_stage, metadata=metadata1)
        request2 = StageRequest(stage=mock_stage, metadata=metadata2)

        # Different metadata should not be equal
        assert request1 != request2

    def test_stage_request_with_complex_metadata(self, mock_stage):
        """Test StageRequest with complex metadata structures."""
        complex_metadata = AbstractStageMetadata(
            {
                "stage_info": {"name": "test_stage", "version": "1.0"},
                "parameters": {"threshold": 0.5, "method": "gaussian"},
                "execution_info": {
                    "start_time": "2025-01-01T00:00:00Z",
                    "duration": 1.5,
                },
            }
        )

        request = StageRequest(stage=mock_stage, metadata=complex_metadata)

        assert request.stage == mock_stage
        assert request.metadata == complex_metadata
        assert request.metadata.data["stage_info"]["name"] == "test_stage"

    def test_stage_request_with_empty_metadata(self, mock_stage):
        """Test StageRequest with empty metadata."""
        empty_metadata = AbstractStageMetadata()
        request = StageRequest(stage=mock_stage, metadata=empty_metadata)

        assert request.stage == mock_stage
        assert request.metadata == empty_metadata
        assert len(request.metadata.data) == 0

    def test_stage_request_inheritance(self, mock_stage, stage_metadata):
        """Test that StageRequest inherits from AbstractStageRequest."""
        request = StageRequest(stage=mock_stage, metadata=stage_metadata)
        assert isinstance(request, AbstractStageRequest)

    def test_stage_request_with_none_stage_and_metadata(self):
        """Test StageRequest with both stage and metadata as None."""
        request = StageRequest(stage=None, metadata=None)

        assert request.stage is None
        assert request.metadata is None
        assert request == StageRequest(stage=None, metadata=None)

    def test_stage_request_serialization_compatibility(
        self, mock_stage, stage_metadata
    ):
        """Test StageRequest for serialization compatibility."""
        request = StageRequest(stage=mock_stage, metadata=stage_metadata)

        # Should be able to access attributes for serialization
        stage = request.stage
        metadata = request.metadata

        assert stage is not None
        assert metadata is not None

        # Should be able to create new request with same data
        new_request = StageRequest(stage=stage, metadata=metadata)
        assert new_request == request

    def test_stage_request_with_various_metadata_types(self, mock_stage):
        """Test StageRequest with various metadata value types."""
        metadata = AbstractStageMetadata(
            {
                "string": "test",
                "int": 42,
                "float": 3.14,
                "bool": True,
                "list": [1, 2, 3],
                "dict": {"inner": "value"},
                "none": None,
            }
        )

        request = StageRequest(stage=mock_stage, metadata=metadata)

        assert request.metadata.data["string"] == "test"
        assert request.metadata.data["int"] == 42
        assert request.metadata.data["float"] == 3.14
        assert request.metadata.data["bool"] is True
        assert request.metadata.data["list"] == [1, 2, 3]
        assert request.metadata.data["dict"] == {"inner": "value"}
        assert request.metadata.data["none"] is None

#
# Created by Isai GORDEEV on 20/09/2025.
#

"""Tests for stage_objects.py module."""

from dataclasses import FrozenInstanceError

import pytest
from saxs.saxs.core.types.abstract_data import BaseDataType
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class TestAbstractStageMetadata:
    """Test cases for AbstractStageMetadata class."""

    def test_stage_metadata_creation_with_dict(self) -> None:
        """Test creating AbstractStageMetadata with dictionary."""
        metadata_dict = {"stage_name": "test_stage", "version": "1.0"}
        metadata = AbstractStageMetadata(values=metadata_dict)

        assert metadata.values == metadata_dict
        assert len(metadata.values) == 2

    def test_stage_metadata_creation_empty(self) -> None:
        """Test creating AbstractStageMetadata with empty dictionary."""
        metadata = AbstractStageMetadata()
        assert metadata.values == {}
        assert len(metadata.values) == 0

    def test_stage_metadata_creation_with_nested_dict(self) -> None:
        """Test creating AbstractStageMetadata with nested dictionary."""
        nested_dict = {
            "stage_info": {"name": "filter_stage", "version": "2.0"},
            "parameters": {"threshold": 0.5, "enabled": True},
        }
        metadata = AbstractStageMetadata(values=nested_dict)
        assert metadata.values == nested_dict

    def test_stage_metadata_describe(self) -> None:
        """Test the describe method."""
        metadata = AbstractStageMetadata(
            values={"key1": "value1", "key2": "value2"},
        )
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "key1" in description
        assert "key2" in description

    def test_stage_metadata_describe_empty(self) -> None:
        """Test describe method with empty metadata."""
        metadata = AbstractStageMetadata()
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "[]" in description  # Empty list representation

    def test_stage_metadata_immutable(self) -> None:
        """Test that AbstractStageMetadata is immutable."""
        metadata = AbstractStageMetadata(values={"key": "value"})

        with pytest.raises(FrozenInstanceError):
            metadata.values = {"new_key": "new_value"}

    def test_stage_metadata_inheritance(self) -> None:
        """Test that AbstractStageMetadata inherits from AData."""
        metadata = AbstractStageMetadata(values={"key": "value"})
        assert isinstance(metadata, BaseDataType)

    def test_stage_metadata_with_various_types(self) -> None:
        """Test AbstractStageMetadata with various value types."""
        complex_dict = {
            "string": "test_stage",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "nested_dict": {"inner": "value"},
            "none": None,
        }
        metadata = AbstractStageMetadata(values=complex_dict)
        assert metadata.values == complex_dict

    def test_stage_metadata_equality(self) -> None:
        """Test AbstractStageMetadata equality comparison."""
        metadata1 = AbstractStageMetadata(values={"key": "value"})
        metadata2 = AbstractStageMetadata(values={"key": "value"})
        metadata3 = AbstractStageMetadata(values={"different": "value"})

        # Same data should be equal
        assert metadata1 == metadata2

        # Different data should not be equal
        assert metadata1 != metadata3

    def test_stage_metadata_with_stage_specific_data(self) -> None:
        """Test AbstractStageMetadata with stage-specific data structures."""
        stage_data = {
            "stage_type": "filter",
            "parameters": {
                "threshold": 0.5,
                "method": "gaussian",
                "enabled": True,
            },
            "execution_info": {
                "start_time": "2025-01-01T00:00:00Z",
                "duration": 1.5,
                "success": True,
            },
            "dependencies": ["preprocessing", "background_subtraction"],
            "output_format": "numpy_array",
        }
        metadata = AbstractStageMetadata(values=stage_data)

        assert metadata.values == stage_data
        assert metadata.values["stage_type"] == "filter"
        assert metadata.values["parameters"]["threshold"] == 0.5
        assert len(metadata.values["dependencies"]) == 2

    def test_stage_metadata_describe_with_complex_data(self) -> None:
        """Test describe method with complex nested data."""
        complex_data = {
            "stage_info": {"name": "test", "version": "1.0"},
            "parameters": {"param1": "value1", "param2": "value2"},
            "results": {"success": True, "count": 42},
        }
        metadata = AbstractStageMetadata(values=complex_data)
        description = metadata.describe()

        assert isinstance(description, str)
        assert "stage_info" in description
        assert "parameters" in description
        assert "results" in description

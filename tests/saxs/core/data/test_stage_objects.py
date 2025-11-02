# Created by Isai Gordeev on 20/09/2025.

"""Tests for stage_objects.py module."""

from dataclasses import FrozenInstanceError

import pytest
from saxs.saxs.core.types.abstract_data import TBaseDataType
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


class TestAbstractStageMetadata:
    """Test cases for AbstractStageMetadata class."""

    def test_stage_metadata_creation_with_dict(self) -> None:
        """Test creating AbstractStageMetadata with dictionary."""
        metadata_dict = {"stage_name": "test_stage", "version": "1.0"}
        metadata = TAbstractStageMetadata(value=metadata_dict)

        assert metadata.value == metadata_dict
        assert len(metadata.value) == 2

    def test_stage_metadata_creation_empty(self) -> None:
        """Test creating AbstractStageMetadata with empty dictionary."""
        metadata = TAbstractStageMetadata()
        assert metadata.value == {}
        assert len(metadata.value) == 0

    def test_stage_metadata_creation_with_nested_dict(self) -> None:
        """Test creating AbstractStageMetadata with nested dictionary."""
        nested_dict = {
            "stage_info": {"name": "filter_stage", "version": "2.0"},
            "parameters": {"threshold": 0.5, "enabled": True},
        }
        metadata = TAbstractStageMetadata(value=nested_dict)
        assert metadata.value == nested_dict

    def test_stage_metadata_describe(self) -> None:
        """Test the describe method."""
        metadata = TAbstractStageMetadata(
            value={"key1": "value1", "key2": "value2"},
        )
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "key1" in description
        assert "key2" in description

    def test_stage_metadata_describe_empty(self) -> None:
        """Test describe method with empty metadata."""
        metadata = TAbstractStageMetadata()
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "[]" in description  # Empty list representation

    def test_stage_metadata_immutable(self) -> None:
        """Test that AbstractStageMetadata is immutable."""
        metadata = TAbstractStageMetadata(value={"key": "value"})

        with pytest.raises(FrozenInstanceError):
            metadata.value = {"new_key": "new_value"}

    def test_stage_metadata_inheritance(self) -> None:
        """Test that AbstractStageMetadata inherits from AData."""
        metadata = TAbstractStageMetadata(value={"key": "value"})
        assert isinstance(metadata, TBaseDataType)

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
        metadata = TAbstractStageMetadata(value=complex_dict)
        assert metadata.value == complex_dict

    def test_stage_metadata_equality(self) -> None:
        """Test AbstractStageMetadata equality comparison."""
        metadata1 = TAbstractStageMetadata(value={"key": "value"})
        metadata2 = TAbstractStageMetadata(value={"key": "value"})
        metadata3 = TAbstractStageMetadata(value={"different": "value"})

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
        metadata = TAbstractStageMetadata(value=stage_data)

        assert metadata.value == stage_data
        assert metadata.value["stage_type"] == "filter"
        assert metadata.value["parameters"]["threshold"] == 0.5
        assert len(metadata.value["dependencies"]) == 2

    def test_stage_metadata_describe_with_complex_data(self) -> None:
        """Test describe method with complex nested data."""
        complex_data = {
            "stage_info": {"name": "test", "version": "1.0"},
            "parameters": {"param1": "value1", "param2": "value2"},
            "results": {"success": True, "count": 42},
        }
        metadata = TAbstractStageMetadata(value=complex_data)
        description = metadata.describe()

        assert isinstance(description, str)
        assert "stage_info" in description
        assert "parameters" in description
        assert "results" in description

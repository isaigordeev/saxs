#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for stage_objects.py module.
"""

from dataclasses import FrozenInstanceError

import pytest

from saxs.saxs.core.data.abstract_data import AData
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata


class TestAbstractStageMetadata:
    """Test cases for AbstractStageMetadata class."""

    def test_stage_metadata_creation_with_dict(self):
        """Test creating AbstractStageMetadata with dictionary."""
        metadata_dict = {"stage_name": "test_stage", "version": "1.0"}
        metadata = AbstractStageMetadata(data=metadata_dict)

        assert metadata.data == metadata_dict
        assert len(metadata.data) == 2

    def test_stage_metadata_creation_empty(self):
        """Test creating AbstractStageMetadata with empty dictionary."""
        metadata = AbstractStageMetadata()
        assert metadata.data == {}
        assert len(metadata.data) == 0

    def test_stage_metadata_creation_with_nested_dict(self):
        """Test creating AbstractStageMetadata with nested dictionary."""
        nested_dict = {
            "stage_info": {"name": "filter_stage", "version": "2.0"},
            "parameters": {"threshold": 0.5, "enabled": True},
        }
        metadata = AbstractStageMetadata(data=nested_dict)
        assert metadata.data == nested_dict

    def test_stage_metadata_describe(self):
        """Test the describe method."""
        metadata = AbstractStageMetadata(
            data={"key1": "value1", "key2": "value2"}
        )
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "key1" in description
        assert "key2" in description

    def test_stage_metadata_describe_empty(self):
        """Test describe method with empty metadata."""
        metadata = AbstractStageMetadata()
        description = metadata.describe()

        assert isinstance(description, str)
        assert "Stage metadata with keys:" in description
        assert "[]" in description  # Empty list representation

    def test_stage_metadata_immutable(self):
        """Test that AbstractStageMetadata is immutable."""
        metadata = AbstractStageMetadata(data={"key": "value"})

        with pytest.raises(FrozenInstanceError):
            metadata.data = {"new_key": "new_value"}

    def test_stage_metadata_inheritance(self):
        """Test that AbstractStageMetadata inherits from AData."""
        metadata = AbstractStageMetadata(data={"key": "value"})
        assert isinstance(metadata, AData)

    def test_stage_metadata_with_various_types(self):
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
        metadata = AbstractStageMetadata(data=complex_dict)
        assert metadata.data == complex_dict

    def test_stage_metadata_equality(self):
        """Test AbstractStageMetadata equality comparison."""
        metadata1 = AbstractStageMetadata(data={"key": "value"})
        metadata2 = AbstractStageMetadata(data={"key": "value"})
        metadata3 = AbstractStageMetadata(data={"different": "value"})

        # Same data should be equal
        assert metadata1 == metadata2

        # Different data should not be equal
        assert metadata1 != metadata3

    def test_stage_metadata_with_stage_specific_data(self):
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
        metadata = AbstractStageMetadata(data=stage_data)

        assert metadata.data == stage_data
        assert metadata.data["stage_type"] == "filter"
        assert metadata.data["parameters"]["threshold"] == 0.5
        assert len(metadata.data["dependencies"]) == 2

    def test_stage_metadata_describe_with_complex_data(self):
        """Test describe method with complex nested data."""
        complex_data = {
            "stage_info": {"name": "test", "version": "1.0"},
            "parameters": {"param1": "value1", "param2": "value2"},
            "results": {"success": True, "count": 42},
        }
        metadata = AbstractStageMetadata(data=complex_data)
        description = metadata.describe()

        assert isinstance(description, str)
        assert "stage_info" in description
        assert "parameters" in description
        assert "results" in description


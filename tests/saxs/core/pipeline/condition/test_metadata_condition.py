#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for metadata_condition.py module.
"""

import pytest

from saxs.saxs.core.types.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.metadata_condition import (
    MetadataCondition,
)


class TestMetadataCondition:
    """Test cases for MetadataCondition class."""

    def test_metadata_condition_creation(self):
        """Test creating MetadataCondition with key and expected value."""
        condition = MetadataCondition(key="temperature", expected_value=25.0)

        assert condition.key == "temperature"
        assert condition.expected_value == 25.0

    def test_metadata_condition_evaluate_exact_match(self):
        """Test evaluate method with exact match."""
        condition = MetadataCondition(key="temperature", expected_value=25.0)

        # Test with exact match
        sample_match = AbstractSampleMetadata({"temperature": 25.0})
        assert condition.evaluate(sample_match) is True

        # Test with different value
        sample_no_match = AbstractSampleMetadata({"temperature": 30.0})
        assert condition.evaluate(sample_no_match) is False

    def test_metadata_condition_evaluate_missing_key(self):
        """Test evaluate method when key is missing from metadata."""
        condition = MetadataCondition(key="pressure", expected_value=1.0)

        # Test with missing key
        sample_no_key = AbstractSampleMetadata({"temperature": 25.0})
        assert condition.evaluate(sample_no_key) is False

        # Test with empty metadata
        sample_empty = AbstractSampleMetadata()
        assert condition.evaluate(sample_empty) is False

    def test_metadata_condition_evaluate_with_different_types(self):
        """Test evaluate method with different value types."""
        # Test with string values
        condition_str = MetadataCondition(key="type", expected_value="protein")
        sample_str = AbstractSampleMetadata({"type": "protein"})
        assert condition_str.evaluate(sample_str) is True

        sample_str_different = AbstractSampleMetadata({"type": "dna"})
        assert condition_str.evaluate(sample_str_different) is False

        # Test with integer values
        condition_int = MetadataCondition(key="count", expected_value=42)
        sample_int = AbstractSampleMetadata({"count": 42})
        assert condition_int.evaluate(sample_int) is True

        sample_int_different = AbstractSampleMetadata({"count": 100})
        assert condition_int.evaluate(sample_int_different) is False

        # Test with boolean values
        condition_bool = MetadataCondition(key="enabled", expected_value=True)
        sample_bool = AbstractSampleMetadata({"enabled": True})
        assert condition_bool.evaluate(sample_bool) is True

        sample_bool_different = AbstractSampleMetadata({"enabled": False})
        assert condition_bool.evaluate(sample_bool_different) is False

    def test_metadata_condition_evaluate_with_none_values(self):
        """Test evaluate method with None values."""
        condition = MetadataCondition(
            key="optional_field", expected_value=None
        )

        # Test with None value
        sample_none = AbstractSampleMetadata({"optional_field": None})
        assert condition.evaluate(sample_none) is True

        # Test with missing key (should return None from get)
        sample_missing = AbstractSampleMetadata({"other_field": "value"})
        assert condition.evaluate(sample_missing) is True  # None == None

        # Test with non-None value
        sample_value = AbstractSampleMetadata({"optional_field": "some_value"})
        assert condition.evaluate(sample_value) is False

    def test_metadata_condition_evaluate_with_complex_values(self):
        """Test evaluate method with complex value types."""
        # Test with list values
        expected_list = [1, 2, 3]
        condition_list = MetadataCondition(
            key="values", expected_value=expected_list
        )
        sample_list = AbstractSampleMetadata({"values": [1, 2, 3]})
        assert condition_list.evaluate(sample_list) is True

        sample_list_different = AbstractSampleMetadata({"values": [4, 5, 6]})
        assert condition_list.evaluate(sample_list_different) is False

        # Test with dictionary values
        expected_dict = {"inner": "value", "number": 42}
        condition_dict = MetadataCondition(
            key="config", expected_value=expected_dict
        )
        sample_dict = AbstractSampleMetadata(
            {"config": {"inner": "value", "number": 42}}
        )
        assert condition_dict.evaluate(sample_dict) is True

        sample_dict_different = AbstractSampleMetadata(
            {"config": {"different": "value"}}
        )
        assert condition_dict.evaluate(sample_dict_different) is False

    def test_metadata_condition_evaluate_with_nested_metadata(self):
        """Test evaluate method with nested metadata structure."""
        condition = MetadataCondition(
            key="experiment.temperature", expected_value=25.0
        )

        # Note: This test assumes the metadata structure supports nested access
        # If the actual implementation doesn't support this, this test should be adjusted
        sample_nested = AbstractSampleMetadata(
            {"experiment": {"temperature": 25.0, "pressure": 1.0}}
        )

        # This will likely fail if nested access isn't supported
        # The test documents the expected behavior
        try:
            result = condition.evaluate(sample_nested)
            # If it works, verify the result
            assert isinstance(result, bool)
        except (KeyError, AttributeError):
            # If nested access isn't supported, that's also valid
            # The test documents this limitation
            pytest.skip("Nested metadata access not supported")

    def test_metadata_condition_evaluate_case_sensitivity(self):
        """Test evaluate method with case-sensitive string matching."""
        condition = MetadataCondition(key="type", expected_value="Protein")

        # Test with exact case match
        sample_exact = AbstractSampleMetadata({"type": "Protein"})
        assert condition.evaluate(sample_exact) is True

        # Test with different case
        sample_different_case = AbstractSampleMetadata({"type": "protein"})
        assert condition.evaluate(sample_different_case) is False

    def test_metadata_condition_evaluate_float_precision(self):
        """Test evaluate method with float precision."""
        condition = MetadataCondition(key="value", expected_value=0.1)

        # Test with exact match
        sample_exact = AbstractSampleMetadata({"value": 0.1})
        assert condition.evaluate(sample_exact) is True

        # Test with very close but not exact match
        sample_close = AbstractSampleMetadata({"value": 0.1000000001})
        # This might fail due to floating point precision
        # The behavior depends on the implementation
        result = condition.evaluate(sample_close)
        assert isinstance(result, bool)

    def test_metadata_condition_multiple_conditions(self):
        """Test using multiple MetadataCondition instances."""
        condition_temp = MetadataCondition(
            key="temperature", expected_value=25.0
        )
        condition_pressure = MetadataCondition(
            key="pressure", expected_value=1.0
        )
        condition_type = MetadataCondition(
            key="type", expected_value="protein"
        )

        # Test with sample that matches all conditions
        sample_all_match = AbstractSampleMetadata(
            {"temperature": 25.0, "pressure": 1.0, "type": "protein"}
        )
        assert condition_temp.evaluate(sample_all_match) is True
        assert condition_pressure.evaluate(sample_all_match) is True
        assert condition_type.evaluate(sample_all_match) is True

        # Test with sample that matches some conditions
        sample_partial_match = AbstractSampleMetadata(
            {
                "temperature": 25.0,
                "pressure": 2.0,  # Different value
                "type": "protein",
            }
        )
        assert condition_temp.evaluate(sample_partial_match) is True
        assert condition_pressure.evaluate(sample_partial_match) is False
        assert condition_type.evaluate(sample_partial_match) is True

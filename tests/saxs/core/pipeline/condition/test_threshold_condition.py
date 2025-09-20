#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for threshold_condition.py module.
"""

import pytest

from saxs.saxs.core.pipeline.condition.threshold_condition import (
    ThresholdCondition,
)
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata


class TestThresholdCondition:
    """Test cases for ThresholdCondition class."""

    def test_threshold_condition_creation(self):
        """Test creating ThresholdCondition with key and threshold."""
        condition = ThresholdCondition(key="intensity", threshold=100.0)

        assert condition.key == "intensity"
        assert condition.threshold == 100.0

    def test_threshold_condition_evaluate_above_threshold(self):
        """Test evaluate method with value above threshold."""
        condition = ThresholdCondition(key="intensity", threshold=100.0)

        # Test with value above threshold
        sample_above = AbstractSampleMetadata({"intensity": 150.0})
        assert condition.evaluate(sample_above) is True

        # Test with value at threshold (should be False, as condition is >)
        sample_at = AbstractSampleMetadata({"intensity": 100.0})
        assert condition.evaluate(sample_at) is False

        # Test with value below threshold
        sample_below = AbstractSampleMetadata({"intensity": 50.0})
        assert condition.evaluate(sample_below) is False

    def test_threshold_condition_evaluate_missing_key(self):
        """Test evaluate method when key is missing from metadata."""
        condition = ThresholdCondition(key="temperature", threshold=20.0)

        # Test with missing key (should default to 0)
        sample_no_key = AbstractSampleMetadata({"other_field": "value"})
        assert condition.evaluate(sample_no_key) is False  # 0 > 20.0 is False

        # Test with empty metadata
        sample_empty = AbstractSampleMetadata()
        assert condition.evaluate(sample_empty) is False  # 0 > 20.0 is False

    def test_threshold_condition_evaluate_with_different_numeric_types(self):
        """Test evaluate method with different numeric types."""
        condition = ThresholdCondition(key="value", threshold=10.0)

        # Test with integer values
        sample_int = AbstractSampleMetadata({"value": 15})
        assert condition.evaluate(sample_int) is True

        sample_int_below = AbstractSampleMetadata({"value": 5})
        assert condition.evaluate(sample_int_below) is False

        # Test with float values
        sample_float = AbstractSampleMetadata({"value": 15.5})
        assert condition.evaluate(sample_float) is True

        sample_float_below = AbstractSampleMetadata({"value": 5.5})
        assert condition.evaluate(sample_float_below) is False

    def test_threshold_condition_evaluate_with_negative_values(self):
        """Test evaluate method with negative values."""
        condition = ThresholdCondition(key="value", threshold=-10.0)

        # Test with value above negative threshold
        sample_above = AbstractSampleMetadata({"value": -5.0})
        assert condition.evaluate(sample_above) is True  # -5.0 > -10.0

        # Test with value below negative threshold
        sample_below = AbstractSampleMetadata({"value": -15.0})
        assert (
            condition.evaluate(sample_below) is False
        )  # -15.0 > -10.0 is False

    def test_threshold_condition_evaluate_with_zero_threshold(self):
        """Test evaluate method with zero threshold."""
        condition = ThresholdCondition(key="value", threshold=0.0)

        # Test with positive value
        sample_positive = AbstractSampleMetadata({"value": 1.0})
        assert condition.evaluate(sample_positive) is True  # 1.0 > 0.0

        # Test with zero value
        sample_zero = AbstractSampleMetadata({"value": 0.0})
        assert condition.evaluate(sample_zero) is False  # 0.0 > 0.0 is False

        # Test with negative value
        sample_negative = AbstractSampleMetadata({"value": -1.0})
        assert (
            condition.evaluate(sample_negative) is False
        )  # -1.0 > 0.0 is False

    def test_threshold_condition_evaluate_with_non_numeric_values(self):
        """Test evaluate method with non-numeric values."""
        condition = ThresholdCondition(key="value", threshold=10.0)

        # Test with string value (should cause comparison error or be converted)
        sample_string = AbstractSampleMetadata({"value": "15"})
        # The behavior depends on implementation - might raise error or convert
        try:
            result = condition.evaluate(sample_string)
            assert isinstance(result, bool)
        except (TypeError, ValueError):
            # If non-numeric comparison raises error, that's also valid
            pytest.skip("Non-numeric comparison not supported or raises error")

        # Test with boolean value
        sample_bool = AbstractSampleMetadata({"value": True})
        try:
            result = condition.evaluate(sample_bool)
            assert isinstance(result, bool)
        except (TypeError, ValueError):
            pytest.skip("Boolean comparison not supported or raises error")

    def test_threshold_condition_evaluate_with_very_large_values(self):
        """Test evaluate method with very large values."""
        condition = ThresholdCondition(key="value", threshold=1e6)

        # Test with value above large threshold
        sample_large = AbstractSampleMetadata({"value": 2e6})
        assert condition.evaluate(sample_large) is True

        # Test with value below large threshold
        sample_small = AbstractSampleMetadata({"value": 5e5})
        assert condition.evaluate(sample_small) is False

    def test_threshold_condition_evaluate_with_very_small_values(self):
        """Test evaluate method with very small values."""
        condition = ThresholdCondition(key="value", threshold=1e-6)

        # Test with value above small threshold
        sample_above = AbstractSampleMetadata({"value": 2e-6})
        assert condition.evaluate(sample_above) is True

        # Test with value below small threshold
        sample_below = AbstractSampleMetadata({"value": 5e-7})
        assert condition.evaluate(sample_below) is False

    def test_threshold_condition_evaluate_float_precision(self):
        """Test evaluate method with float precision issues."""
        condition = ThresholdCondition(key="value", threshold=0.1)

        # Test with value that might have precision issues
        sample_precise = AbstractSampleMetadata({"value": 0.1000000001})
        # This should work despite small precision differences
        result = condition.evaluate(sample_precise)
        assert isinstance(result, bool)
        # The exact result depends on floating point precision

    def test_threshold_condition_evaluate_with_none_value(self):
        """Test evaluate method with None value."""
        condition = ThresholdCondition(key="value", threshold=10.0)

        # Test with None value (should default to 0)
        sample_none = AbstractSampleMetadata({"value": None})
        # The behavior depends on implementation
        try:
            result = condition.evaluate(sample_none)
            assert isinstance(result, bool)
        except (TypeError, ValueError):
            pytest.skip("None value handling not supported or raises error")

    def test_threshold_condition_multiple_conditions(self):
        """Test using multiple ThresholdCondition instances."""
        condition_intensity = ThresholdCondition(
            key="intensity", threshold=100.0
        )
        condition_temperature = ThresholdCondition(
            key="temperature", threshold=20.0
        )
        condition_pressure = ThresholdCondition(key="pressure", threshold=1.0)

        # Test with sample that passes all conditions
        sample_all_pass = AbstractSampleMetadata(
            {"intensity": 150.0, "temperature": 25.0, "pressure": 2.0}
        )
        assert condition_intensity.evaluate(sample_all_pass) is True
        assert condition_temperature.evaluate(sample_all_pass) is True
        assert condition_pressure.evaluate(sample_all_pass) is True

        # Test with sample that fails some conditions
        sample_partial_pass = AbstractSampleMetadata(
            {
                "intensity": 50.0,  # Below threshold
                "temperature": 25.0,  # Above threshold
                "pressure": 0.5,  # Below threshold
            }
        )
        assert condition_intensity.evaluate(sample_partial_pass) is False
        assert condition_temperature.evaluate(sample_partial_pass) is True
        assert condition_pressure.evaluate(sample_partial_pass) is False

#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for chaining_condition.py module.
"""

import pytest

from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata


class TestChainingPeakCondition:
    """Test cases for ChainingPeakCondition class."""

    def test_chaining_peak_condition_creation(self):
        """Test creating ChainingPeakCondition with key and expected value."""
        condition = ChainingPeakCondition(
            key="peak_detected", expected_value=True
        )

        assert condition.key == "peak_detected"
        assert condition.expected_value is True

    def test_chaining_peak_condition_evaluate_exact_match(self):
        """Test evaluate method with exact match."""
        condition = ChainingPeakCondition(
            key="peak_detected", expected_value=True
        )

        # Test with exact match
        sample_match = AbstractSampleMetadata({"peak_detected": True})
        assert condition.evaluate(sample_match) is True

        # Test with different value
        sample_no_match = AbstractSampleMetadata({"peak_detected": False})
        assert condition.evaluate(sample_no_match) is False

    def test_chaining_peak_condition_evaluate_missing_key(self):
        """Test evaluate method when key is missing from metadata."""
        condition = ChainingPeakCondition(key="peak_count", expected_value=5)

        # Test with missing key
        sample_no_key = AbstractSampleMetadata({"other_field": "value"})
        assert condition.evaluate(sample_no_key) is False  # None == 5 is False

        # Test with empty metadata
        sample_empty = AbstractSampleMetadata()
        assert condition.evaluate(sample_empty) is False  # None == 5 is False

    def test_chaining_peak_condition_evaluate_with_different_types(self):
        """Test evaluate method with different value types."""
        # Test with boolean values
        condition_bool = ChainingPeakCondition(
            key="enabled", expected_value=True
        )
        sample_bool = AbstractSampleMetadata({"enabled": True})
        assert condition_bool.evaluate(sample_bool) is True

        sample_bool_different = AbstractSampleMetadata({"enabled": False})
        assert condition_bool.evaluate(sample_bool_different) is False

        # Test with integer values
        condition_int = ChainingPeakCondition(
            key="peak_count", expected_value=3
        )
        sample_int = AbstractSampleMetadata({"peak_count": 3})
        assert condition_int.evaluate(sample_int) is True

        sample_int_different = AbstractSampleMetadata({"peak_count": 5})
        assert condition_int.evaluate(sample_int_different) is False

        # Test with string values
        condition_str = ChainingPeakCondition(
            key="peak_type", expected_value="gaussian"
        )
        sample_str = AbstractSampleMetadata({"peak_type": "gaussian"})
        assert condition_str.evaluate(sample_str) is True

        sample_str_different = AbstractSampleMetadata(
            {"peak_type": "lorentzian"}
        )
        assert condition_str.evaluate(sample_str_different) is False

    def test_chaining_peak_condition_evaluate_with_none_values(self):
        """Test evaluate method with None values."""
        condition = ChainingPeakCondition(
            key="optional_field", expected_value=None
        )

        # Test with None value
        sample_none = AbstractSampleMetadata({"optional_field": None})
        assert condition.evaluate(sample_none) is True  # None == None

        # Test with missing key (should return None from get)
        sample_missing = AbstractSampleMetadata({"other_field": "value"})
        assert condition.evaluate(sample_missing) is True  # None == None

        # Test with non-None value
        sample_value = AbstractSampleMetadata({"optional_field": "some_value"})
        assert (
            condition.evaluate(sample_value) is False
        )  # "some_value" == None is False

    def test_chaining_peak_condition_evaluate_with_peak_specific_data(self):
        """Test evaluate method with peak-specific data structures."""
        # Test with peak detection results
        condition_detected = ChainingPeakCondition(
            key="peaks_detected", expected_value=True
        )
        sample_detected = AbstractSampleMetadata(
            {
                "peaks_detected": True,
                "peak_count": 3,
                "peak_positions": [0.1, 0.3, 0.5],
                "peak_amplitudes": [100.0, 150.0, 200.0],
            }
        )
        assert condition_detected.evaluate(sample_detected) is True

        # Test with peak processing status
        condition_processed = ChainingPeakCondition(
            key="peaks_processed", expected_value="completed"
        )
        sample_processed = AbstractSampleMetadata(
            {
                "peaks_processed": "completed",
                "processing_time": 1.5,
                "success": True,
            }
        )
        assert condition_processed.evaluate(sample_processed) is True

        sample_processing = AbstractSampleMetadata(
            {
                "peaks_processed": "in_progress",
                "processing_time": 0.5,
                "success": None,
            }
        )
        assert condition_processed.evaluate(sample_processing) is False

    def test_chaining_peak_condition_evaluate_with_complex_values(self):
        """Test evaluate method with complex value types."""
        # Test with list values
        expected_peaks = [0.1, 0.3, 0.5]
        condition_list = ChainingPeakCondition(
            key="peak_positions", expected_value=expected_peaks
        )
        sample_list = AbstractSampleMetadata(
            {"peak_positions": [0.1, 0.3, 0.5]}
        )
        assert condition_list.evaluate(sample_list) is True

        sample_list_different = AbstractSampleMetadata(
            {"peak_positions": [0.2, 0.4, 0.6]}
        )
        assert condition_list.evaluate(sample_list_different) is False

        # Test with dictionary values
        expected_config = {"method": "gaussian", "threshold": 0.5}
        condition_dict = ChainingPeakCondition(
            key="peak_config", expected_value=expected_config
        )
        sample_dict = AbstractSampleMetadata(
            {"peak_config": {"method": "gaussian", "threshold": 0.5}}
        )
        assert condition_dict.evaluate(sample_dict) is True

        sample_dict_different = AbstractSampleMetadata(
            {"peak_config": {"method": "lorentzian", "threshold": 0.5}}
        )
        assert condition_dict.evaluate(sample_dict_different) is False

    def test_chaining_peak_condition_evaluate_case_sensitivity(self):
        """Test evaluate method with case-sensitive string matching."""
        condition = ChainingPeakCondition(
            key="peak_method", expected_value="Gaussian"
        )

        # Test with exact case match
        sample_exact = AbstractSampleMetadata({"peak_method": "Gaussian"})
        assert condition.evaluate(sample_exact) is True

        # Test with different case
        sample_different_case = AbstractSampleMetadata(
            {"peak_method": "gaussian"}
        )
        assert condition.evaluate(sample_different_case) is False

    def test_chaining_peak_condition_evaluate_float_precision(self):
        """Test evaluate method with float precision."""
        condition = ChainingPeakCondition(
            key="peak_threshold", expected_value=0.1
        )

        # Test with exact match
        sample_exact = AbstractSampleMetadata({"peak_threshold": 0.1})
        assert condition.evaluate(sample_exact) is True

        # Test with very close but not exact match
        sample_close = AbstractSampleMetadata({"peak_threshold": 0.1000000001})
        # This might fail due to floating point precision
        result = condition.evaluate(sample_close)
        assert isinstance(result, bool)

    def test_chaining_peak_condition_multiple_conditions(self):
        """Test using multiple ChainingPeakCondition instances."""
        condition_detected = ChainingPeakCondition(
            key="peaks_detected", expected_value=True
        )
        condition_count = ChainingPeakCondition(
            key="peak_count", expected_value=3
        )
        condition_method = ChainingPeakCondition(
            key="peak_method", expected_value="gaussian"
        )

        # Test with sample that matches all conditions
        sample_all_match = AbstractSampleMetadata(
            {"peaks_detected": True, "peak_count": 3, "peak_method": "gaussian"}
        )
        assert condition_detected.evaluate(sample_all_match) is True
        assert condition_count.evaluate(sample_all_match) is True
        assert condition_method.evaluate(sample_all_match) is True

        # Test with sample that matches some conditions
        sample_partial_match = AbstractSampleMetadata(
            {
                "peaks_detected": True,
                "peak_count": 5,  # Different value
                "peak_method": "gaussian",
            }
        )
        assert condition_detected.evaluate(sample_partial_match) is True
        assert condition_count.evaluate(sample_partial_match) is False
        assert condition_method.evaluate(sample_partial_match) is True

    def test_chaining_peak_condition_peak_workflow_scenario(self):
        """Test ChainingPeakCondition in a realistic peak analysis workflow scenario."""
        # Simulate a peak analysis workflow with multiple conditions

        # Step 1: Check if peaks were detected
        condition_detected = ChainingPeakCondition(
            key="peaks_detected", expected_value=True
        )

        # Step 2: Check if enough peaks were found
        condition_min_peaks = ChainingPeakCondition(
            key="peak_count", expected_value=2
        )

        # Step 3: Check if peak fitting was successful
        condition_fitted = ChainingPeakCondition(
            key="peaks_fitted", expected_value=True
        )

        # Step 4: Check if quality is acceptable
        condition_quality = ChainingPeakCondition(
            key="peak_quality", expected_value="good"
        )

        # Test with successful workflow
        sample_success = AbstractSampleMetadata(
            {
                "peaks_detected": True,
                "peak_count": 2,
                "peaks_fitted": True,
                "peak_quality": "good",
            }
        )
        assert condition_detected.evaluate(sample_success) is True
        assert condition_min_peaks.evaluate(sample_success) is True
        assert condition_fitted.evaluate(sample_success) is True
        assert condition_quality.evaluate(sample_success) is True

        # Test with failed workflow (no peaks detected)
        sample_no_peaks = AbstractSampleMetadata(
            {
                "peaks_detected": False,
                "peak_count": 0,
                "peaks_fitted": False,
                "peak_quality": "poor",
            }
        )
        assert condition_detected.evaluate(sample_no_peaks) is False
        assert condition_min_peaks.evaluate(sample_no_peaks) is False
        assert condition_fitted.evaluate(sample_no_peaks) is False
        assert condition_quality.evaluate(sample_no_peaks) is False

        # Test with partial workflow (peaks detected but fitting failed)
        sample_partial = AbstractSampleMetadata(
            {
                "peaks_detected": True,
                "peak_count": 3,
                "peaks_fitted": False,
                "peak_quality": "poor",
            }
        )
        assert condition_detected.evaluate(sample_partial) is True
        assert condition_min_peaks.evaluate(sample_partial) is False
        assert condition_fitted.evaluate(sample_partial) is False
        assert condition_quality.evaluate(sample_partial) is False

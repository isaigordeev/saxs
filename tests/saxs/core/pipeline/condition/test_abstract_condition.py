#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for abstract_condition.py module.
"""

import pytest
from abc import ABC, abstractmethod

from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata


class TestSampleCondition:
    """Test cases for SampleCondition abstract base class."""

    def test_sample_condition_is_abstract(self):
        """Test that SampleCondition cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SampleCondition()

    def test_sample_condition_has_evaluate_method(self):
        """Test that SampleCondition has the abstract evaluate method."""
        assert hasattr(SampleCondition, "evaluate")
        assert callable(getattr(SampleCondition, "evaluate"))

    def test_concrete_implementation_works(self):
        """Test that a concrete implementation of SampleCondition works correctly."""

        class ConcreteCondition(SampleCondition):
            def __init__(self, threshold: float):
                self.threshold = threshold

            def evaluate(self, sample: AbstractSampleMetadata) -> bool:
                return sample.metadata.get("value", 0) > self.threshold

        condition = ConcreteCondition(threshold=10.0)

        # Test with sample that passes condition
        sample_pass = AbstractSampleMetadata({"value": 15.0})
        assert condition.evaluate(sample_pass) is True

        # Test with sample that fails condition
        sample_fail = AbstractSampleMetadata({"value": 5.0})
        assert condition.evaluate(sample_fail) is False

    def test_concrete_implementation_without_evaluate_fails(self):
        """Test that a concrete implementation without evaluate method fails."""

        class IncompleteCondition(SampleCondition):
            def __init__(self, threshold: float):
                self.threshold = threshold

            # Missing evaluate method

        with pytest.raises(TypeError):
            IncompleteCondition(threshold=10.0)

    def test_condition_with_complex_evaluation(self):
        """Test condition with complex evaluation logic."""

        class ComplexCondition(SampleCondition):
            def __init__(
                self, min_value: float, max_value: float, required_keys: list
            ):
                self.min_value = min_value
                self.max_value = max_value
                self.required_keys = required_keys

            def evaluate(self, sample: AbstractSampleMetadata) -> bool:
                metadata = sample.metadata

                # Check if all required keys are present
                if not all(key in metadata for key in self.required_keys):
                    return False

                # Check if value is within range
                value = metadata.get("value", 0)
                return self.min_value <= value <= self.max_value

        condition = ComplexCondition(
            min_value=10.0,
            max_value=100.0,
            required_keys=["value", "type", "quality"],
        )

        # Test with valid sample
        valid_sample = AbstractSampleMetadata(
            {"value": 50.0, "type": "protein", "quality": "high"}
        )
        assert condition.evaluate(valid_sample) is True

        # Test with sample missing required keys
        invalid_sample1 = AbstractSampleMetadata({"value": 50.0})
        assert condition.evaluate(invalid_sample1) is False

        # Test with sample outside value range
        invalid_sample2 = AbstractSampleMetadata(
            {"value": 150.0, "type": "protein", "quality": "high"}
        )
        assert condition.evaluate(invalid_sample2) is False

    def test_condition_with_empty_metadata(self):
        """Test condition evaluation with empty metadata."""

        class SimpleCondition(SampleCondition):
            def evaluate(self, sample: AbstractSampleMetadata) -> bool:
                return "test_key" in sample.metadata

        condition = SimpleCondition()
        empty_sample = AbstractSampleMetadata()

        assert condition.evaluate(empty_sample) is False

    def test_condition_inheritance_chain(self):
        """Test condition with inheritance chain."""

        class BaseCondition(SampleCondition):
            def __init__(self, base_threshold: float):
                self.base_threshold = base_threshold

            def evaluate(self, sample: AbstractSampleMetadata) -> bool:
                return (
                    sample.metadata.get("base_value", 0) > self.base_threshold
                )

        class ExtendedCondition(BaseCondition):
            def __init__(
                self, base_threshold: float, extended_threshold: float
            ):
                super().__init__(base_threshold)
                self.extended_threshold = extended_threshold

            def evaluate(self, sample: AbstractSampleMetadata) -> bool:
                # Check base condition
                base_result = super().evaluate(sample)
                if not base_result:
                    return False

                # Check extended condition
                return (
                    sample.metadata.get("extended_value", 0)
                    > self.extended_threshold
                )

        condition = ExtendedCondition(
            base_threshold=10.0, extended_threshold=20.0
        )

        # Test with sample that passes both conditions
        valid_sample = AbstractSampleMetadata(
            {"base_value": 15.0, "extended_value": 25.0}
        )
        assert condition.evaluate(valid_sample) is True

        # Test with sample that fails base condition
        invalid_sample1 = AbstractSampleMetadata(
            {"base_value": 5.0, "extended_value": 25.0}
        )
        assert condition.evaluate(invalid_sample1) is False

        # Test with sample that fails extended condition
        invalid_sample2 = AbstractSampleMetadata(
            {"base_value": 15.0, "extended_value": 10.0}
        )
        assert condition.evaluate(invalid_sample2) is False

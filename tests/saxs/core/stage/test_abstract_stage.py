#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for abstract_stage.py module.
"""

import pytest
from abc import ABC, abstractmethod
from unittest.mock import Mock

from saxs.saxs.core.stage.abstract_stage import (
    AbstractStage,
    AbstractConditionalStage,
)
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition


class TestAbstractStage:
    """Test cases for AbstractStage abstract base class."""

    def test_abstract_stage_is_abstract(self):
        """Test that AbstractStage cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractStage()

    def test_abstract_stage_has_process_method(self):
        """Test that AbstractStage has the process method."""
        assert hasattr(AbstractStage, "process")
        assert callable(getattr(AbstractStage, "process"))

    def test_abstract_stage_has_process_abstract_method(self):
        """Test that AbstractStage has the abstract _process method."""
        assert hasattr(AbstractStage, "_process")
        assert callable(getattr(AbstractStage, "_process"))

    def test_abstract_stage_has_get_next_stage_method(self):
        """Test that AbstractStage has the get_next_stage method."""
        assert hasattr(AbstractStage, "get_next_stage")
        assert callable(getattr(AbstractStage, "get_next_stage"))

    def test_concrete_implementation_works(self, saxs_sample):
        """Test that a concrete implementation of AbstractStage works correctly."""

        class ConcreteStage(AbstractStage):
            def __init__(self, name: str = "concrete_stage"):
                self.metadata = AbstractStageMetadata({"name": name})

            def _process(self, stage_data):
                # Simple pass-through for testing
                return stage_data

            def get_next_stage(self):
                return []

        stage = ConcreteStage()

        # Test process method
        result = stage.process(saxs_sample)
        assert result == saxs_sample

        # Test get_next_stage method
        next_stages = stage.get_next_stage()
        assert next_stages == []

    def test_concrete_implementation_without_process_fails(self):
        """Test that a concrete implementation without _process method fails."""

        class IncompleteStage(AbstractStage):
            def __init__(self):
                self.metadata = AbstractStageMetadata({"name": "incomplete"})

            # Missing _process method

        with pytest.raises(TypeError):
            IncompleteStage()

    def test_concrete_implementation_with_metadata(self, saxs_sample):
        """Test concrete implementation with metadata."""

        class MetadataStage(AbstractStage):
            def __init__(self, stage_name: str, version: str = "1.0"):
                self.metadata = AbstractStageMetadata(
                    {
                        "name": stage_name,
                        "version": version,
                        "type": "test_stage",
                    }
                )

            def _process(self, stage_data):
                return stage_data

            def get_next_stage(self):
                return []

        stage = MetadataStage("test_stage", "2.0")

        # Test metadata
        assert stage.metadata.data["name"] == "test_stage"
        assert stage.metadata.data["version"] == "2.0"
        assert stage.metadata.data["type"] == "test_stage"

        # Test processing
        result = stage.process(saxs_sample)
        assert result == saxs_sample

    def test_concrete_implementation_with_next_stages(self, saxs_sample):
        """Test concrete implementation that returns next stages."""

        class ChainingStage(AbstractStage):
            def __init__(self, next_stages=None):
                self.metadata = AbstractStageMetadata(
                    {"name": "chaining_stage"}
                )
                self.next_stages = next_stages or []

            def _process(self, stage_data):
                return stage_data

            def get_next_stage(self):
                return self.next_stages

        # Test with no next stages
        stage1 = ChainingStage()
        assert stage1.get_next_stage() == []

        # Test with next stages
        next_stage1 = Mock()
        next_stage2 = Mock()
        stage2 = ChainingStage([next_stage1, next_stage2])
        assert stage2.get_next_stage() == [next_stage1, next_stage2]

    def test_concrete_implementation_with_processing_logic(self, saxs_sample):
        """Test concrete implementation with actual processing logic."""

        class ProcessingStage(AbstractStage):
            def __init__(self, multiplier: float = 2.0):
                self.metadata = AbstractStageMetadata(
                    {"name": "processing_stage"}
                )
                self.multiplier = multiplier

            def _process(self, stage_data):
                # Modify the intensity values
                current_intensity = stage_data.get_intensity_array()
                new_intensity = current_intensity * self.multiplier
                return stage_data.set_intensity(new_intensity)

            def get_next_stage(self):
                return []

        stage = ProcessingStage(multiplier=3.0)

        # Test processing
        result = stage.process(saxs_sample)

        # Check that intensity was modified
        original_intensity = saxs_sample.get_intensity_array()
        result_intensity = result.get_intensity_array()

        np.testing.assert_array_equal(
            result_intensity, original_intensity * 3.0
        )

    def test_concrete_implementation_with_exception_handling(self, saxs_sample):
        """Test concrete implementation with exception handling."""

        class ErrorStage(AbstractStage):
            def __init__(self, should_raise: bool = False):
                self.metadata = AbstractStageMetadata({"name": "error_stage"})
                self.should_raise = should_raise

            def _process(self, stage_data):
                if self.should_raise:
                    raise ValueError("Processing failed")
                return stage_data

            def get_next_stage(self):
                return []

        # Test normal processing
        stage_normal = ErrorStage(should_raise=False)
        result = stage_normal.process(saxs_sample)
        assert result == saxs_sample

        # Test error processing
        stage_error = ErrorStage(should_raise=True)
        with pytest.raises(ValueError, match="Processing failed"):
            stage_error.process(saxs_sample)


class TestAbstractConditionalStage:
    """Test cases for AbstractConditionalStage class."""

    def test_abstract_conditional_stage_creation(self, mock_stage):
        """Test creating AbstractConditionalStage."""
        # Create a mock condition
        condition = Mock(spec=SampleCondition)
        condition.evaluate.return_value = True

        conditional_stage = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition
        )

        assert conditional_stage.chaining_stage == mock_stage
        assert conditional_stage.condition == condition

    def test_abstract_conditional_stage_inheritance(self, mock_stage):
        """Test that AbstractConditionalStage inherits from AbstractStage."""
        condition = Mock(spec=SampleCondition)
        conditional_stage = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition
        )

        assert isinstance(conditional_stage, AbstractStage)

    def test_abstract_conditional_stage_has_metadata(self, mock_stage):
        """Test that AbstractConditionalStage has metadata attribute."""
        condition = Mock(spec=SampleCondition)
        conditional_stage = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition
        )

        # Should have metadata attribute (inherited from AbstractStage)
        assert hasattr(conditional_stage, "metadata")

    def test_abstract_conditional_stage_condition_evaluation(
        self, mock_stage, saxs_sample
    ):
        """Test AbstractConditionalStage condition evaluation."""
        # Create a mock condition that returns True
        condition_true = Mock(spec=SampleCondition)
        condition_true.evaluate.return_value = True

        conditional_stage_true = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition_true
        )

        # Test with condition that returns True
        condition_true.evaluate.assert_not_called()  # Not called yet

        # Create a mock condition that returns False
        condition_false = Mock(spec=SampleCondition)
        condition_false.evaluate.return_value = False

        conditional_stage_false = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition_false
        )

        # Test with condition that returns False
        condition_false.evaluate.assert_not_called()  # Not called yet

    def test_abstract_conditional_stage_with_different_conditions(
        self, mock_stage, saxs_sample
    ):
        """Test AbstractConditionalStage with different condition types."""
        # Test with metadata condition
        from saxs.saxs.core.pipeline.condition.metadata_condition import (
            MetadataCondition,
        )

        metadata_condition = MetadataCondition(
            key="test_key", expected_value="test_value"
        )
        conditional_stage_metadata = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=metadata_condition
        )

        # Test with threshold condition
        from saxs.saxs.core.pipeline.condition.threshold_condition import (
            ThresholdCondition,
        )

        threshold_condition = ThresholdCondition(
            key="test_value", threshold=10.0
        )
        conditional_stage_threshold = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=threshold_condition
        )

        # Both should be valid AbstractConditionalStage instances
        assert isinstance(conditional_stage_metadata, AbstractConditionalStage)
        assert isinstance(conditional_stage_threshold, AbstractConditionalStage)

    def test_abstract_conditional_stage_with_none_values(self):
        """Test AbstractConditionalStage with None values."""
        # Test with None chaining stage
        condition = Mock(spec=SampleCondition)
        conditional_stage_none_stage = AbstractConditionalStage(
            chaining_stage=None, condition=condition
        )

        assert conditional_stage_none_stage.chaining_stage is None
        assert conditional_stage_none_stage.condition == condition

        # Test with None condition
        mock_stage = Mock()
        conditional_stage_none_condition = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=None
        )

        assert conditional_stage_none_condition.chaining_stage == mock_stage
        assert conditional_stage_none_condition.condition is None

    def test_abstract_conditional_stage_immutability(self, mock_stage):
        """Test that AbstractConditionalStage attributes are immutable."""
        condition = Mock(spec=SampleCondition)
        conditional_stage = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition
        )

        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            conditional_stage.chaining_stage = None

        with pytest.raises(AttributeError):
            conditional_stage.condition = None

    def test_abstract_conditional_stage_equality(self, mock_stage):
        """Test AbstractConditionalStage equality comparison."""
        condition1 = Mock(spec=SampleCondition)
        condition2 = Mock(spec=SampleCondition)

        conditional_stage1 = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition1
        )

        conditional_stage2 = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition1
        )

        conditional_stage3 = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition2
        )

        # Same stage and condition should be equal
        assert conditional_stage1 == conditional_stage2

        # Different conditions should not be equal
        assert conditional_stage1 != conditional_stage3

    def test_abstract_conditional_stage_hash(self, mock_stage):
        """Test AbstractConditionalStage hashability."""
        condition = Mock(spec=SampleCondition)
        conditional_stage = AbstractConditionalStage(
            chaining_stage=mock_stage, condition=condition
        )

        # Should be hashable (can be used as dict key)
        conditional_stage_dict = {conditional_stage: "test_value"}
        assert conditional_stage_dict[conditional_stage] == "test_value"

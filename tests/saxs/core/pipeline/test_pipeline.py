#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for pipeline.py module.
"""

import pytest
from unittest.mock import Mock, MagicMock

from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.core.pipeline.scheduler.insertion_policy import (
    AlwaysInsertPolicy,
)
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata


class TestPipeline:
    """Test cases for Pipeline class."""

    def test_pipeline_creation_default(self):
        """Test creating Pipeline with default parameters."""
        pipeline = Pipeline()

        assert pipeline.init_stages == []
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert pipeline.scheduler._queue == []

    def test_pipeline_creation_with_stages(self, mock_stage):
        """Test creating Pipeline with initial stages."""
        stages = [mock_stage, mock_stage]
        pipeline = Pipeline(init_stages=stages)

        assert pipeline.init_stages == stages
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert list(pipeline.scheduler._queue) == stages

    def test_pipeline_creation_with_custom_scheduler(self, mock_stage):
        """Test creating Pipeline with custom scheduler."""
        custom_scheduler = Mock()
        stages = [mock_stage]
        pipeline = Pipeline(init_stages=stages, scheduler=custom_scheduler)

        assert pipeline.init_stages == stages
        assert pipeline.scheduler == custom_scheduler

    def test_pipeline_creation_with_none_stages(self):
        """Test creating Pipeline with None stages."""
        pipeline = Pipeline(init_stages=None)

        assert pipeline.init_stages == []
        assert isinstance(pipeline.scheduler, BaseScheduler)

    def test_pipeline_with_stages_class_method(self, mock_stage):
        """Test Pipeline.with_stages class method."""
        stage1 = mock_stage
        stage2 = Mock()

        pipeline = Pipeline.with_stages(stage1, stage2)

        assert pipeline.init_stages == [stage1, stage2]
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert list(pipeline.scheduler._queue) == [stage1, stage2]

    def test_pipeline_with_stages_class_method_empty(self):
        """Test Pipeline.with_stages class method with no stages."""
        pipeline = Pipeline.with_stages()

        assert pipeline.init_stages == []
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert pipeline.scheduler._queue == []

    def test_pipeline_with_stages_class_method_custom_scheduler(
        self, mock_stage
    ):
        """Test Pipeline.with_stages class method with custom scheduler."""
        custom_scheduler = Mock()
        pipeline = Pipeline.with_stages(mock_stage, scheduler=custom_scheduler)

        assert pipeline.init_stages == [mock_stage]
        assert pipeline.scheduler == custom_scheduler

    def test_pipeline_run_with_no_stages(self, saxs_sample):
        """Test Pipeline run with no stages."""
        pipeline = Pipeline()
        result = pipeline.run(saxs_sample)

        # Should return the original sample unchanged
        assert result == saxs_sample

    def test_pipeline_run_with_single_stage(self, saxs_sample, mock_stage):
        """Test Pipeline run with single stage."""
        # Mock the stage's process method
        mock_stage.process.return_value = saxs_sample

        pipeline = Pipeline(init_stages=[mock_stage])
        result = pipeline.run(saxs_sample)

        # Should call process on the stage
        mock_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_multiple_stages(self, saxs_sample):
        """Test Pipeline run with multiple stages."""
        # Create mock stages
        stage1 = Mock()
        stage2 = Mock()
        stage3 = Mock()

        # Set up return values
        modified_sample = saxs_sample.set_q_values([0.1, 0.2, 0.3])
        stage1.process.return_value = modified_sample
        stage2.process.return_value = modified_sample
        stage3.process.return_value = modified_sample

        pipeline = Pipeline(init_stages=[stage1, stage2, stage3])
        result = pipeline.run(saxs_sample)

        # Should call process on all stages in order
        stage1.process.assert_called_once_with(saxs_sample)
        stage2.process.assert_called_once_with(modified_sample)
        stage3.process.assert_called_once_with(modified_sample)
        assert result == modified_sample

    def test_pipeline_run_with_custom_scheduler(self, saxs_sample, mock_stage):
        """Test Pipeline run with custom scheduler."""
        # Create custom scheduler mock
        custom_scheduler = Mock()
        custom_scheduler.run.return_value = saxs_sample

        pipeline = Pipeline(
            init_stages=[mock_stage], scheduler=custom_scheduler
        )
        result = pipeline.run(saxs_sample)

        # Should call the custom scheduler's run method
        custom_scheduler.run.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_stage_requests(self, saxs_sample):
        """Test Pipeline run with stages that request additional stages."""
        # Create mock stages
        stage1 = Mock()
        additional_stage = Mock()

        # Set up stage request
        from saxs.saxs.core.pipeline.scheduler.stage_request import StageRequest
        from saxs.saxs.core.data.stage_objects import AbstractStageMetadata

        stage_metadata = AbstractStageMetadata({"type": "additional"})
        stage_request = StageRequest(
            stage=additional_stage, metadata=stage_metadata
        )

        stage1.get_next_stage.return_value = [stage_request]
        additional_stage.get_next_stage.return_value = []

        # Set up process methods
        stage1.process.return_value = saxs_sample
        additional_stage.process.return_value = saxs_sample

        pipeline = Pipeline(init_stages=[stage1])
        result = pipeline.run(saxs_sample)

        # Should process all stages including the requested one
        stage1.process.assert_called_once_with(saxs_sample)
        additional_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_scheduler_exception(
        self, saxs_sample, mock_stage
    ):
        """Test Pipeline run when scheduler raises an exception."""
        # Create custom scheduler that raises exception
        custom_scheduler = Mock()
        custom_scheduler.run.side_effect = ValueError("Scheduler failed")

        pipeline = Pipeline(
            init_stages=[mock_stage], scheduler=custom_scheduler
        )

        # Should propagate the exception
        with pytest.raises(ValueError, match="Scheduler failed"):
            pipeline.run(saxs_sample)

    def test_pipeline_run_with_stage_exception(self, saxs_sample, mock_stage):
        """Test Pipeline run when a stage raises an exception."""
        # Mock stage to raise exception
        mock_stage.process.side_effect = ValueError("Stage processing failed")

        pipeline = Pipeline(init_stages=[mock_stage])

        # Should propagate the exception
        with pytest.raises(ValueError, match="Stage processing failed"):
            pipeline.run(saxs_sample)

    def test_pipeline_immutability_after_creation(self, mock_stage):
        """Test that Pipeline attributes are not modified after creation."""
        stages = [mock_stage]
        scheduler = Mock()

        pipeline = Pipeline(init_stages=stages, scheduler=scheduler)

        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            pipeline.init_stages = []

        with pytest.raises(AttributeError):
            pipeline.scheduler = None

    def test_pipeline_with_different_sample_types(self, q_values, intensity):
        """Test Pipeline with different sample types."""
        from saxs.saxs.core.data.sample import SAXSSample

        # Create different sample types
        sample1 = SAXSSample(q_values=q_values, intensity=intensity)
        sample2 = SAXSSample(q_values=q_values, intensity=intensity)

        # Create mock stage that returns different sample
        mock_stage = Mock()
        mock_stage.process.return_value = sample2

        pipeline = Pipeline(init_stages=[mock_stage])
        result = pipeline.run(sample1)

        # Should return the processed sample
        assert result == sample2
        assert result is not sample1

    def test_pipeline_with_empty_stage_list(self, saxs_sample):
        """Test Pipeline with empty stage list."""
        pipeline = Pipeline(init_stages=[])
        result = pipeline.run(saxs_sample)

        # Should return the original sample unchanged
        assert result == saxs_sample

    def test_pipeline_with_none_stages_parameter(self, saxs_sample):
        """Test Pipeline with None stages parameter."""
        pipeline = Pipeline(init_stages=None)
        result = pipeline.run(saxs_sample)

        # Should return the original sample unchanged
        assert result == saxs_sample

    def test_pipeline_scheduler_initialization(self, mock_stage):
        """Test that Pipeline properly initializes the scheduler."""
        stages = [mock_stage]
        pipeline = Pipeline(init_stages=stages)

        # Scheduler should be initialized with the stages
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert list(pipeline.scheduler._queue) == stages

    def test_pipeline_with_stages_class_method_multiple_calls(self, mock_stage):
        """Test multiple calls to Pipeline.with_stages class method."""
        stage1 = mock_stage
        stage2 = Mock()

        # Create multiple pipelines
        pipeline1 = Pipeline.with_stages(stage1)
        pipeline2 = Pipeline.with_stages(stage1, stage2)

        # Should create independent pipelines
        assert pipeline1.init_stages == [stage1]
        assert pipeline2.init_stages == [stage1, stage2]
        assert pipeline1 is not pipeline2

    def test_pipeline_run_with_complex_workflow(self, saxs_sample):
        """Test Pipeline run with a complex multi-stage workflow."""
        # Create mock stages for a complex workflow
        preprocessing_stage = Mock()
        filtering_stage = Mock()
        peak_detection_stage = Mock()
        analysis_stage = Mock()

        # Set up stage chain
        preprocessing_stage.get_next_stage.return_value = []
        filtering_stage.get_next_stage.return_value = []
        peak_detection_stage.get_next_stage.return_value = []
        analysis_stage.get_next_stage.return_value = []

        # Set up process methods
        intermediate_sample1 = saxs_sample.set_q_values([0.1, 0.2, 0.3])
        intermediate_sample2 = intermediate_sample1.set_intensity(
            [100, 200, 300]
        )
        final_sample = intermediate_sample2.set_intensity_error([10, 20, 30])

        preprocessing_stage.process.return_value = intermediate_sample1
        filtering_stage.process.return_value = intermediate_sample2
        peak_detection_stage.process.return_value = final_sample
        analysis_stage.process.return_value = final_sample

        # Create pipeline with all stages
        pipeline = Pipeline(
            init_stages=[
                preprocessing_stage,
                filtering_stage,
                peak_detection_stage,
                analysis_stage,
            ]
        )

        result = pipeline.run(saxs_sample)

        # Should process all stages in order
        preprocessing_stage.process.assert_called_once_with(saxs_sample)
        filtering_stage.process.assert_called_once_with(intermediate_sample1)
        peak_detection_stage.process.assert_called_once_with(
            intermediate_sample2
        )
        analysis_stage.process.assert_called_once_with(final_sample)
        assert result == final_sample

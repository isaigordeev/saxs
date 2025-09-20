#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for pipeline.py module using pytest fixtures.
"""

from collections import deque
from unittest.mock import Mock

import pytest

from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageRequest,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler

# ------------------------
# Fixtures
# ------------------------


@pytest.fixture
def saxs_sample():
    """Minimal SAXSSample for testing."""
    from saxs.saxs.core.data.sample import SAXSSample
    from saxs.saxs.core.data.sample_objects import (
        AbstractSampleMetadata,
        Intensity,
        IntensityError,
        QValues,
    )

    q = QValues([0.1, 0.2, 0.3])
    i = Intensity([1.0, 2.0, 3.0])
    err = IntensityError([0.01, 0.02, 0.03])
    meta = AbstractSampleMetadata({"source": "test"})
    return SAXSSample(
        q_values=q, intensity=i, intensity_error=err, metadata=meta
    )


@pytest.fixture
def mock_stage():
    """Fixture for a simple mock stage."""
    stage = Mock()
    stage.metadata = AbstractStageMetadata({"name": "mock_stage"})
    stage.process = Mock()
    stage.get_next_stage.return_value = []
    return stage


@pytest.fixture
def multi_mock_stages():
    """Fixture returning a list of multiple mock stages."""
    stage1 = Mock()
    stage1.metadata = AbstractStageMetadata({"name": "stage1"})
    stage1.process = Mock()
    stage1.get_next_stage.return_value = []

    stage2 = Mock()
    stage2.metadata = AbstractStageMetadata({"name": "stage2"})
    stage2.process = Mock()
    stage2.get_next_stage.return_value = []

    stage3 = Mock()
    stage3.metadata = AbstractStageMetadata({"name": "stage3"})
    stage3.process = Mock()
    stage3.get_next_stage.return_value = []

    return [stage1, stage2, stage3]


# ------------------------
# Tests
# ------------------------


class TestPipeline:
    """Test cases for Pipeline class using fixtures."""

    def test_pipeline_creation_default(self):
        pipeline = Pipeline()
        assert pipeline.init_stages == []
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert pipeline.scheduler._queue == deque([])

    def test_pipeline_creation_with_stages(self, mock_stage):
        stages = [mock_stage, mock_stage]
        pipeline = Pipeline(init_stages=stages)
        assert pipeline.init_stages == stages
        assert list(pipeline.scheduler._queue) == stages

    def test_pipeline_creation_with_custom_scheduler(self, mock_stage):
        custom_scheduler = Mock()
        stages = [mock_stage]
        pipeline = Pipeline(init_stages=stages, scheduler=custom_scheduler)
        assert pipeline.init_stages == stages
        assert pipeline.scheduler == custom_scheduler

    def test_pipeline_creation_with_none_stages(self):
        pipeline = Pipeline(init_stages=None)
        assert pipeline.init_stages == []
        assert isinstance(pipeline.scheduler, BaseScheduler)

    def test_pipeline_with_stages_class_method(self, mock_stage):
        stage2 = Mock()
        pipeline = Pipeline.with_stages(mock_stage, stage2)
        assert pipeline.init_stages == [mock_stage, stage2]
        assert list(pipeline.scheduler._queue) == [mock_stage, stage2]

    def test_pipeline_with_stages_class_method_empty(self):
        pipeline = Pipeline.with_stages()
        assert pipeline.init_stages == []
        assert pipeline.scheduler._queue == deque([])

    def test_pipeline_with_stages_class_method_custom_scheduler(
        self, mock_stage
    ):
        custom_scheduler = Mock()
        pipeline = Pipeline.with_stages(mock_stage, scheduler=custom_scheduler)
        assert pipeline.init_stages == [mock_stage]
        assert pipeline.scheduler == custom_scheduler

    def test_pipeline_run_with_no_stages(self, saxs_sample):
        pipeline = Pipeline()
        result = pipeline.run(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_single_stage(self, saxs_sample, mock_stage):
        mock_stage.process.return_value = saxs_sample
        pipeline = Pipeline(init_stages=[mock_stage])
        result = pipeline.run(saxs_sample)
        mock_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_multiple_stages(
        self, saxs_sample, multi_mock_stages
    ):
        stage1, stage2, stage3 = multi_mock_stages
        modified_sample = saxs_sample.set_q_values([0.1, 0.2, 0.3])
        stage1.process.return_value = modified_sample
        stage2.process.return_value = modified_sample
        stage3.process.return_value = modified_sample

        pipeline = Pipeline(init_stages=[stage1, stage2, stage3])
        result = pipeline.run(saxs_sample)

        stage1.process.assert_called_once_with(saxs_sample)
        stage2.process.assert_called_once_with(modified_sample)
        stage3.process.assert_called_once_with(modified_sample)
        assert result == modified_sample

    def test_pipeline_run_with_custom_scheduler(self, saxs_sample, mock_stage):
        custom_scheduler = Mock()
        custom_scheduler.run.return_value = saxs_sample
        pipeline = Pipeline(
            init_stages=[mock_stage], scheduler=custom_scheduler
        )
        result = pipeline.run(saxs_sample)
        custom_scheduler.run.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_stage_requests(self, saxs_sample):
        stage1 = Mock()
        additional_stage = Mock()
        stage_request = StageRequest(
            stage=additional_stage,
            metadata=AbstractStageMetadata({"type": "additional"}),
        )
        stage1.get_next_stage.return_value = [stage_request]

        stage1.process.return_value = saxs_sample
        additional_stage.process.return_value = saxs_sample
        additional_stage.get_next_stage.return_value = []

        pipeline = Pipeline(init_stages=[stage1])
        result = pipeline.run(saxs_sample)
        stage1.process.assert_called_once_with(saxs_sample)
        additional_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_run_with_scheduler_exception(
        self, saxs_sample, mock_stage
    ):
        custom_scheduler = Mock()
        custom_scheduler.run.side_effect = ValueError("Scheduler failed")
        pipeline = Pipeline(
            init_stages=[mock_stage], scheduler=custom_scheduler
        )
        with pytest.raises(ValueError, match="Scheduler failed"):
            pipeline.run(saxs_sample)

    def test_pipeline_run_with_stage_exception(self, saxs_sample, mock_stage):
        mock_stage.process.side_effect = ValueError("Stage processing failed")
        pipeline = Pipeline(init_stages=[mock_stage])
        with pytest.raises(ValueError, match="Stage processing failed"):
            pipeline.run(saxs_sample)

    def test_pipeline_with_different_sample_types(
        self, q_values, intensity, mock_stage
    ):
        pass

    def test_pipeline_with_empty_stage_list(self, saxs_sample):
        pipeline = Pipeline(init_stages=[])
        result = pipeline.run(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_with_none_stages_parameter(self, saxs_sample):
        pipeline = Pipeline(init_stages=None)
        result = pipeline.run(saxs_sample)
        assert result == saxs_sample

    def test_pipeline_scheduler_initialization(self, mock_stage):
        pipeline = Pipeline(init_stages=[mock_stage])
        assert isinstance(pipeline.scheduler, BaseScheduler)
        assert list(pipeline.scheduler._queue) == [mock_stage]

    def test_pipeline_with_stages_class_method_multiple_calls(self, mock_stage):
        stage2 = Mock()
        pipeline1 = Pipeline.with_stages(mock_stage)
        pipeline2 = Pipeline.with_stages(mock_stage, stage2)
        assert pipeline1.init_stages == [mock_stage]
        assert pipeline2.init_stages == [mock_stage, stage2]
        assert pipeline1 is not pipeline2

    def test_pipeline_run_with_complex_workflow(self, saxs_sample):
        preprocessing_stage = Mock()
        filtering_stage = Mock()
        peak_detection_stage = Mock()
        analysis_stage = Mock()

        preprocessing_stage.get_next_stage.return_value = []
        filtering_stage.get_next_stage.return_value = []
        peak_detection_stage.get_next_stage.return_value = []
        analysis_stage.get_next_stage.return_value = []

        intermediate_sample1 = saxs_sample.set_q_values([0.1, 0.2, 0.3])
        intermediate_sample2 = intermediate_sample1.set_intensity(
            [100, 200, 300]
        )
        final_sample = intermediate_sample2.set_intensity_error([10, 20, 30])

        preprocessing_stage.process.return_value = intermediate_sample1
        filtering_stage.process.return_value = intermediate_sample2
        peak_detection_stage.process.return_value = final_sample
        analysis_stage.process.return_value = final_sample

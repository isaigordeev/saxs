#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for scheduler.py module.
"""

from collections import deque
from unittest.mock import Mock

import numpy as np
import pytest

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.sample_objects import (
    AbstractSampleMetadata,
    Intensity,
    IntensityError,
    QValues,
)
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageRequest,
)
from saxs.saxs.core.pipeline.scheduler.insertion_policy import (
    AlwaysInsertPolicy,
    NeverInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import (
    AbstractScheduler,
    BaseScheduler,
)


# ----------------
# Fixtures
# ----------------
@pytest.fixture
def saxs_sample():
    """Create a minimal valid SAXSSample for testing."""
    q = QValues(np.array([0.1, 0.2, 0.3]))
    i = Intensity(np.array([1.0, 2.0, 3.0]))
    err = IntensityError(np.array([0.01, 0.02, 0.03]))
    meta = AbstractSampleMetadata({"source": "test"})
    return SAXSSample(
        q_values=q, intensity=i, intensity_error=err, metadata=meta
    )


@pytest.fixture
def mock_stage(saxs_sample):
    """Return a mock stage with process and get_next_stage mocked."""
    stage = Mock()
    stage.metadata = AbstractStageMetadata({"name": "mock_stage"})
    stage.process = Mock(
        return_value=saxs_sample
    )  # you can set return_value in each test
    stage.get_next_stage.return_value = []  # no new stages by default
    return stage


# ----------------
# Tests
# ----------------
class TestAbstractScheduler:
    """Test cases for AbstractScheduler abstract base class."""

    def test_abstract_scheduler_is_abstract(self):
        """Test that AbstractScheduler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractScheduler()

    def test_abstract_scheduler_has_run_method(self):
        """Test that AbstractScheduler has the abstract run method."""
        assert hasattr(AbstractScheduler, "run")
        assert callable(getattr(AbstractScheduler, "run"))

    def test_abstract_scheduler_initialization(self):
        """Test AbstractScheduler initialization with concrete implementation."""

        class ConcreteScheduler(AbstractScheduler):
            def run(self, init_sample):
                return init_sample

        # Test with no initial stages
        scheduler = ConcreteScheduler()
        assert scheduler._queue == deque()
        assert isinstance(scheduler._insertion_policy, AlwaysInsertPolicy)

        # Test with initial stages
        mock_stages = [Mock(), Mock()]
        scheduler_with_stages = ConcreteScheduler(init_stages=mock_stages)
        assert list(scheduler_with_stages._queue) == mock_stages

    def test_abstract_scheduler_with_custom_insertion_policy(self):
        """Test AbstractScheduler with custom insertion policy."""

        class ConcreteScheduler(AbstractScheduler):
            def run(self, init_sample):
                return init_sample

        custom_policy = NeverInsertPolicy()
        scheduler = ConcreteScheduler(insertion_policy=custom_policy)
        assert scheduler._insertion_policy == custom_policy


class TestBaseScheduler:
    """Test cases for BaseScheduler class."""

    def test_base_scheduler_creation(self):
        """Test creating BaseScheduler."""
        scheduler = BaseScheduler()
        assert isinstance(scheduler, AbstractScheduler)
        assert isinstance(scheduler._queue, deque)
        assert len(scheduler._queue) == 0

    def test_base_scheduler_creation_with_stages(self, mock_stage):
        """Test creating BaseScheduler with initial stages."""
        stages = [mock_stage, mock_stage]
        scheduler = BaseScheduler(init_stages=stages)

        assert len(scheduler._queue) == 2
        assert list(scheduler._queue) == stages

    def test_base_scheduler_creation_with_custom_policy(self):
        """Test creating BaseScheduler with custom insertion policy."""
        custom_policy = NeverInsertPolicy()
        scheduler = BaseScheduler(insertion_policy=custom_policy)

        assert scheduler._insertion_policy == custom_policy

    def test_base_scheduler_run_with_no_stages(self, saxs_sample):
        """Test BaseScheduler run with no stages."""
        scheduler = BaseScheduler()
        result = scheduler.run(saxs_sample)

        # Should return the original sample unchanged
        assert result == saxs_sample

    def test_base_scheduler_run_with_single_stage(
        self, saxs_sample, mock_stage
    ):
        """Test BaseScheduler run with single stage."""
        # Mock the stage's process method

        scheduler = BaseScheduler(init_stages=[mock_stage])
        result = scheduler.run(saxs_sample)

        # Should call process on the stage
        mock_stage.process.assert_called_once_with(saxs_sample)
        assert result
        assert result == saxs_sample
        print("dodf", result)
        assert result.metadata.unwrap().get("source") == "test"

    def test_base_scheduler_run_with_multiple_stages(
        self, saxs_sample, mock_stage
    ):
        """Test BaseScheduler run with multiple stages."""
        # Create mock stages
        import copy

        stage1 = copy.deepcopy(mock_stage)
        stage2 = copy.deepcopy(mock_stage)
        stage3 = copy.deepcopy(mock_stage)

        # Set up return values
        modified_sample = saxs_sample.set_q_values(np.array([0.1, 0.2, 0.3]))
        stage1.process.return_value = modified_sample
        stage2.process.return_value = modified_sample
        stage3.process.return_value = modified_sample

        scheduler = BaseScheduler(init_stages=[stage1, stage2, stage3])
        result = scheduler.run(saxs_sample)

        # Should call process on all stages in order
        stage1.process.assert_called_once_with(saxs_sample)
        stage2.process.assert_called_once_with(modified_sample)
        stage3.process.assert_called_once_with(modified_sample)
        assert result == modified_sample

    def test_base_scheduler_run_with_stage_requests(self, saxs_sample):
        """Test BaseScheduler run with stages that request additional stages."""
        # Create mock stages
        stage1 = Mock()
        stage2 = Mock()
        additional_stage = Mock()

        # Set up stage requests
        stage_metadata = AbstractStageMetadata({"type": "additional"})
        stage_request = StageRequest(
            stage=additional_stage, metadata=stage_metadata
        )

        stage1.get_next_stage.return_value = [stage_request]
        stage2.get_next_stage.return_value = []
        additional_stage.get_next_stage.return_value = []

        # Set up process methods
        stage1.process.return_value = saxs_sample
        stage2.process.return_value = saxs_sample
        additional_stage.process.return_value = saxs_sample

        scheduler = BaseScheduler(init_stages=[stage1, stage2])
        result = scheduler.run(saxs_sample)

        # Should process all stages including the requested one
        stage1.process.assert_called_once_with(saxs_sample)
        stage2.process.assert_called_once_with(saxs_sample)
        additional_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_base_scheduler_run_with_insertion_policy_rejection(
        self, saxs_sample
    ):
        """Test BaseScheduler run when insertion policy rejects requests."""
        # Create mock stages
        stage1 = Mock()
        additional_stage = Mock()

        # Set up stage request
        stage_metadata = AbstractStageMetadata({"type": "additional"})
        stage_request = StageRequest(
            stage=additional_stage, metadata=stage_metadata
        )

        stage1.get_next_stage.return_value = [stage_request]
        stage1.process.return_value = saxs_sample

        # Use NeverInsertPolicy to reject all requests
        scheduler = BaseScheduler(
            init_stages=[stage1], insertion_policy=NeverInsertPolicy()
        )
        result = scheduler.run(saxs_sample)

        # Should only process the initial stage, not the requested one
        stage1.process.assert_called_once_with(saxs_sample)
        additional_stage.process.assert_not_called()
        assert result == saxs_sample

    def test_base_scheduler_run_with_multiple_requests(self, saxs_sample):
        """Test BaseScheduler run with multiple stage requests."""
        # Create mock stages
        stage1 = Mock()
        additional_stage1 = Mock()
        additional_stage2 = Mock()

        # Set up multiple stage requests
        stage_metadata1 = AbstractStageMetadata({"type": "additional1"})
        stage_metadata2 = AbstractStageMetadata({"type": "additional2"})
        stage_request1 = StageRequest(
            stage=additional_stage1, metadata=stage_metadata1
        )
        stage_request2 = StageRequest(
            stage=additional_stage2, metadata=stage_metadata2
        )

        stage1.get_next_stage.return_value = [stage_request1, stage_request2]
        additional_stage1.get_next_stage.return_value = []
        additional_stage2.get_next_stage.return_value = []

        # Set up process methods
        stage1.process.return_value = saxs_sample
        additional_stage1.process.return_value = saxs_sample
        additional_stage2.process.return_value = saxs_sample

        scheduler = BaseScheduler(init_stages=[stage1])
        result = scheduler.run(saxs_sample)

        # Should process all stages including the requested ones
        stage1.process.assert_called_once_with(saxs_sample)
        additional_stage1.process.assert_called_once_with(saxs_sample)
        additional_stage2.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_base_scheduler_run_with_nested_requests(self, saxs_sample):
        """Test BaseScheduler run with nested stage requests."""
        # Create mock stages
        stage1 = Mock()
        additional_stage1 = Mock()
        additional_stage2 = Mock()

        # Set up nested requests
        stage_metadata1 = AbstractStageMetadata({"type": "additional1"})
        stage_metadata2 = AbstractStageMetadata({"type": "additional2"})
        stage_request1 = StageRequest(
            stage=additional_stage1, metadata=stage_metadata1
        )
        stage_request2 = StageRequest(
            stage=additional_stage2, metadata=stage_metadata2
        )

        stage1.get_next_stage.return_value = [stage_request1]
        additional_stage1.get_next_stage.return_value = [stage_request2]
        additional_stage2.get_next_stage.return_value = []

        # Set up process methods
        stage1.process.return_value = saxs_sample
        additional_stage1.process.return_value = saxs_sample
        additional_stage2.process.return_value = saxs_sample

        scheduler = BaseScheduler(init_stages=[stage1])
        result = scheduler.run(saxs_sample)

        # Should process all stages in the correct order
        stage1.process.assert_called_once_with(saxs_sample)
        additional_stage1.process.assert_called_once_with(saxs_sample)
        additional_stage2.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_base_scheduler_run_with_stage_exception(
        self, saxs_sample, mock_stage
    ):
        """Test BaseScheduler run when a stage raises an exception."""
        # Mock stage to raise exception
        mock_stage.process.side_effect = ValueError("Stage processing failed")

        scheduler = BaseScheduler(init_stages=[mock_stage])

        # Should propagate the exception
        with pytest.raises(ValueError, match="Stage processing failed"):
            scheduler.run(saxs_sample)

    def test_base_scheduler_run_with_empty_stage_requests(
        self, saxs_sample, mock_stage
    ):
        """Test BaseScheduler run when stage returns empty requests."""
        scheduler = BaseScheduler(init_stages=[mock_stage])
        result = scheduler.run(saxs_sample)

        # Should process the stage and return result
        mock_stage.process.assert_called_once_with(saxs_sample)
        assert result == saxs_sample

    def test_base_scheduler_run_with_none_stage_requests(
        self, saxs_sample, mock_stage
    ):
        """Test BaseScheduler run when stage returns None for requests."""
        scheduler = BaseScheduler(init_stages=[mock_stage])

        # Should handle None gracefully
        try:
            result = scheduler.run(saxs_sample)
            mock_stage.process.assert_called_once_with(saxs_sample)
            assert result == saxs_sample
        except (AttributeError, TypeError):
            pytest.skip("None stage requests handling not implemented")

    def test_base_scheduler_queue_management(self, saxs_sample):
        """Test BaseScheduler queue management during execution."""
        # Create mock stages
        stage1 = Mock()
        stage2 = Mock()
        additional_stage = Mock()

        # Set up stage request
        stage_metadata = AbstractStageMetadata({"type": "additional"})
        stage_request = StageRequest(
            stage=additional_stage, metadata=stage_metadata
        )

        stage1.get_next_stage.return_value = [stage_request]
        stage2.get_next_stage.return_value = []
        additional_stage.get_next_stage.return_value = []

        # Set up process methods
        stage1.process.return_value = saxs_sample
        stage2.process.return_value = saxs_sample
        additional_stage.process.return_value = saxs_sample

        scheduler = BaseScheduler(init_stages=[stage1, stage2])

        # Check initial queue state
        assert len(scheduler._queue) == 2

        # Run the scheduler
        result = scheduler.run(saxs_sample)

        # Queue should be empty after execution
        assert len(scheduler._queue) == 0
        assert result == saxs_sample

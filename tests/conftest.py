"""Pytest configuration and shared fixtures for SAXS testing."""

from unittest.mock import MagicMock

import numpy as np
import pytest

from saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.types.sample import SAXSSample, SampleMetadata


@pytest.fixture
def sample_q_values():
    """Create sample Q values for testing."""
    return np.array([0.1, 0.2, 0.3, 0.4, 0.5])


@pytest.fixture
def sample_intensity():
    """Create sample intensity values for testing."""
    return np.array([100.0, 150.0, 200.0, 180.0, 120.0])


@pytest.fixture
def sample_intensity_error():
    """Create sample intensity error values for testing."""
    return np.array([5.0, 7.5, 10.0, 9.0, 6.0])


@pytest.fixture
def saxs_sample(sample_q_values, sample_intensity, sample_intensity_error):
    """Create a complete SAXSSample for testing."""
    return SAXSSample(
        q_values=sample_q_values,
        intensity=sample_intensity,
        intensity_err=sample_intensity_error,
        metadata=SampleMetadata(),
    )


@pytest.fixture
def mock_stage():
    """Create a mock stage for testing."""
    stage = MagicMock(spec=IAbstractStage)
    stage.request_stage.return_value = []
    stage.metadata = None
    return stage


@pytest.fixture
def stage_request(mock_stage):
    """Create a StageApprovalRequest for testing."""
    return StageApprovalRequest(stage=mock_stage)

#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Pytest configuration and shared fixtures for SAXS testing.
"""

import numpy as np
import pytest
from dataclasses import dataclass
from typing import Dict, Any, Optional

from saxs.saxs.core.data.sample_objects import (
    QValues,
    Intensity,
    IntensityError,
    AbstractSampleMetadata,
)
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.pipeline.scheduler.stage_request import StageRequest


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
def sample_metadata():
    """Create sample metadata for testing."""
    return {"temperature": 25.0, "pressure": 1.0, "wavelength": 1.54}


@pytest.fixture
def q_values(sample_q_values):
    """Create QValues object for testing."""
    return QValues(sample_q_values)


@pytest.fixture
def intensity(sample_intensity):
    """Create Intensity object for testing."""
    return Intensity(sample_intensity)


@pytest.fixture
def intensity_error(sample_intensity_error):
    """Create IntensityError object for testing."""
    return IntensityError(sample_intensity_error)


@pytest.fixture
def metadata(sample_metadata):
    """Create AbstractSampleMetadata object for testing."""
    return AbstractSampleMetadata(sample_metadata)


@pytest.fixture
def saxs_sample(q_values, intensity, intensity_error, metadata):
    """Create a complete SAXSSample for testing."""
    return SAXSSample(
        q_values=q_values,
        intensity=intensity,
        intensity_error=intensity_error,
        metadata=metadata,
    )


@pytest.fixture
def saxs_sample_minimal(q_values, intensity):
    """Create a minimal SAXSSample for testing (no error or metadata)."""
    return SAXSSample(q_values=q_values, intensity=intensity)


@pytest.fixture
def stage_metadata():
    """Create AbstractStageMetadata for testing."""
    return AbstractStageMetadata({"stage_name": "test_stage", "version": "1.0"})


@pytest.fixture
def mock_stage():
    """Create a mock stage for testing."""

    class MockStage(AbstractStage):
        def __init__(self, name: str = "mock_stage"):
            self.metadata = AbstractStageMetadata({"name": name})

        def _process(self, stage_data: SAXSSample) -> SAXSSample:
            # Simple pass-through for testing
            return stage_data

        def get_next_stage(self):
            return []

    return MockStage()


@pytest.fixture
def stage_request(mock_stage, stage_metadata):
    """Create a StageRequest for testing."""
    return StageRequest(stage=mock_stage, metadata=stage_metadata)


@pytest.fixture
def empty_metadata():
    """Create empty metadata for testing."""
    return AbstractSampleMetadata({})


@pytest.fixture
def complex_metadata():
    """Create complex metadata for testing."""
    return AbstractSampleMetadata(
        {
            "temperature": 25.0,
            "pressure": 1.0,
            "wavelength": 1.54,
            "sample_id": "test_001",
            "measurement_time": 3600,
            "detector_distance": 1000.0,
            "beam_size": 0.5,
            "exposure_time": 1.0,
            "frames": 100,
            "flux": 1e12,
        }
    )

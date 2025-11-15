# Created by Isai Gordeev on 20/09/2025.

"""Tests for find_peak_stage.py module."""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from saxs.logging.logger import logger
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import (
    Intensity,
    IntensityError,
    QValues,
    SampleMetadata,
)
from saxs.saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    AProcessPeakStage,
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    intensity = np.array(
        [10.0, 15.0, 20.0, 25.0, 30.0, 25.0, 20.0, 15.0, 10.0, 5.0],
    )
    intensity_error = np.array(
        [1.0, 1.5, 2.0, 2.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5],
    )

    return SAXSSample(
        q_values=QValues(q_values),
        intensity=Intensity(intensity),
        intensity_error=IntensityError(intensity_error),
        metadata=SampleMetadata({"source": "test"}),
    )


@pytest.fixture
def mock_condition():
    """Create a mock condition for testing."""
    condition = Mock(spec=SampleCondition)
    condition.evaluate.return_value = True
    return condition


@pytest.fixture
def mock_chaining_condition():
    """Create a mock condition for testing."""
    return ChainingPeakCondition("peaks")


@pytest.fixture
def mock_chaining_stage():
    """Create a mock chaining stage for testing."""
    return Mock(spec=AProcessPeakStage)


@pytest.fixture
def find_peaks_stage(mock_chaining_stage, mock_condition):
    """Create FindAllPeaksStage instance for testing."""
    return FindPeakStage(
        chaining_stage=mock_chaining_stage,
        condition=mock_condition,
    )


@pytest.fixture
def find_peaks_chaining_stage(mock_chaining_stage, mock_chaining_condition):
    """Create FindAllPeaksStage instance for testing."""
    return FindPeakStage(
        chaining_stage=AProcessPeakStage,
        condition=mock_chaining_condition,
    )


class TestFindAllPeaksStage:
    """Test cases for FindAllPeaksStage class."""

    def test_find_peaks_stage_creation(
        self,
        mock_chaining_stage,
        mock_condition,
    ) -> None:
        """Test creating FindAllPeaksStage."""
        stage = FindPeakStage(
            chaining_stage=mock_chaining_stage,
            condition=mock_condition,
        )

        assert stage.chaining_stage == mock_chaining_stage
        assert stage.condition == mock_condition

    def test_find_peaks_stage_inheritance(
        self,
        mock_chaining_stage,
        mock_condition,
    ) -> None:
        """Test that FindAllPeaksStage inherits from AbstractConditionalStage."""
        stage = FindPeakStage(
            chaining_stage=mock_chaining_stage,
            condition=mock_condition,
        )
        from saxs.saxs.core.stage.abstract_cond_stage import (
            AbstractConditionalStage,
        )

        assert isinstance(stage, AbstractConditionalStage)

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_basic(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage process method with basic functionality."""
        # Mock find_peaks to return known peaks
        mock_find_peaks.return_value = (
            np.array([4]),
            {"peak_heights": [30.0]},
        )

        result = find_peaks_stage.process(sample_data)

        # Should return a SAXSSample
        assert isinstance(result, SAXSSample)
        assert result is not sample_data  # Should be a new instance

        # Should have called find_peaks
        mock_find_peaks.assert_called_once()

        # Check that find_peaks was called with intensity array
        call_args = mock_find_peaks.call_args
        assert "x" in call_args[1]
        np.testing.assert_array_equal(
            call_args[1]["x"],
            sample_data.get_intensity_array(),
        )

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_peaks_detection(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage process method with peak detection."""
        # Mock find_peaks to return multiple peaks
        mock_find_peaks.return_value = (
            np.array([2, 4, 6]),
            {"peak_heights": [20.0, 30.0, 20.0]},
        )

        result = find_peaks_stage.process(sample_data)

        # Should have peaks in metadata
        assert "peaks" in result.get_metadata_dict()
        peaks = result.get_metadata_dict()["peaks"]
        assert isinstance(peaks, np.ndarray)
        assert len(peaks) == 3
        np.testing.assert_array_equal(peaks, np.array([2, 4, 6]))

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_no_peaks(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage process method when no peaks are found."""
        # Mock find_peaks to return no peaks
        mock_find_peaks.return_value = (np.array([]), {})

        result = find_peaks_stage.process(sample_data)

        # Should have empty peaks array in metadata
        assert "peaks" in result.get_metadata_dict()
        peaks = result.get_metadata_dict()["peaks"]
        assert isinstance(peaks, np.ndarray)
        assert len(peaks) == 0

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_preserves_other_data(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test that FindAllPeaksStage preserves other sample data."""
        mock_find_peaks.return_value = (
            np.array([4]),
            {"peak_heights": [30.0]},
        )

        result = find_peaks_stage.process(sample_data)

        # Q values should be preserved
        np.testing.assert_array_equal(
            result.get_q_values_array(),
            sample_data.get_q_values_array(),
        )

        # Intensity should be preserved
        np.testing.assert_array_equal(
            result.get_intensity_array(),
            sample_data.get_intensity_array(),
        )

        # Intensity error should be preserved
        np.testing.assert_array_equal(
            result.get_intensity_error_array(),
            sample_data.get_intensity_error_array(),
        )

    def test_find_peaks_stage_process_metadata_handling(
        self,
        sample_data,
        find_peaks_stage,
    ) -> None:
        result = find_peaks_stage.process(sample_data)

        result_metadata = result.get_metadata_dict()

        assert "peaks" in result_metadata

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_with_different_peaks(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with different peak configurations."""
        # Test with single peak
        mock_find_peaks.return_value = (
            np.array([4]),
            {"peak_heights": [30.0]},
        )
        result1 = find_peaks_stage.process(sample_data)
        assert len(result1.get_metadata_dict()["peaks"]) == 1

        # Test with multiple peaks
        mock_find_peaks.return_value = (
            np.array([1, 4, 7]),
            {"peak_heights": [15.0, 30.0, 20.0]},
        )
        result2 = find_peaks_stage.process(sample_data)
        assert len(result2.get_metadata_dict()["peaks"]) == 3

    @patch("saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks")
    def test_find_peaks_stage_process_with_find_peaks_error(
        self,
        mock_find_peaks,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage when find_peaks raises an exception."""
        mock_find_peaks.side_effect = ValueError("Peak detection failed")

        with pytest.raises(ValueError, match="Peak detection failed"):
            find_peaks_stage.process(sample_data)

    def test_find_peaks_stage_process_with_minimal_data(
        self,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with minimal sample data."""
        q_values = np.array([0.1, 0.2])
        intensity = np.array([10.0, 8.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (np.array([]), {})

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            assert len(result.get_q_values_array()) == 2

    def test_find_peaks_stage_process_immutability(
        self,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test that FindAllPeaksStage doesn't modify the original sample."""
        original_intensity = sample_data.get_intensity_array().copy()
        original_q_values = sample_data.get_q_values_array().copy()
        original_metadata = sample_data.get_metadata_dict().copy()

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([4]),
                {"peak_heights": [30.0]},
            )

            result = find_peaks_stage.process(sample_data)

            # Original sample should be unchanged
            np.testing.assert_array_equal(
                sample_data.get_intensity_array(),
                original_intensity,
            )
            np.testing.assert_array_equal(
                sample_data.get_q_values_array(),
                original_q_values,
            )
            assert sample_data.get_metadata_dict() == original_metadata

            # Result should have peaks added to metadata
            assert "peaks" in result.get_metadata_dict()

    def test_find_peaks_stage_process_consistency(
        self,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test that FindAllPeaksStage produces consistent results."""
        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([4]),
                {"peak_heights": [30.0]},
            )

            result1 = find_peaks_stage.process(sample_data)
            result2 = find_peaks_stage.process(sample_data)

            # Should produce identical results
            assert (
                result1.get_metadata_dict()["peaks"].tolist()
                == result2.get_metadata_dict()["peaks"].tolist()
            )

    def test_find_peaks_stage_process_with_none_error(
        self, find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with sample that has None intensity error."""
        q_values = np.array([0.1, 0.2, 0.3])
        intensity = np.array([10.0, 8.0, 6.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
            intensity_error=None,
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([1]),
                {"peak_heights": [8.0]},
            )

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            assert result.get_intensity_error() is None

    def test_find_peaks_stage_process_with_empty_data(
        self, find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with empty sample data."""
        sample = SAXSSample(
            q_values=QValues(np.array([])),
            intensity=Intensity(np.array([])),
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (np.array([]), {})

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            assert len(result.get_q_values_array()) == 0
            assert len(result.get_intensity_array()) == 0

    def test_find_peaks_stage_process_with_different_data_types(
        self,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with different data types."""
        # Test with float32 data
        q_values = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        intensity = np.array([10.0, 8.0, 6.0], dtype=np.float32)

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([1]),
                {"peak_heights": [8.0]},
            )

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            assert result.get_q_values_array().dtype == np.float32
            assert result.get_intensity_array().dtype == np.float32

    def test_find_peaks_stage_process_with_negative_values(
        self,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with negative intensity values."""
        q_values = np.array([0.1, 0.2, 0.3])
        intensity = np.array([-10.0, 0.0, 10.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([2]),
                {"peak_heights": [10.0]},
            )

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            np.testing.assert_array_equal(
                result.get_intensity_array(),
                intensity,
            )

    def test_find_peaks_stage_process_with_inf_values(
        self, find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with infinite values."""
        q_values = np.array([0.1, 0.2, 0.3])
        intensity = np.array([10.0, np.inf, 6.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
        )

        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([1]),
                {"peak_heights": [np.inf]},
            )

            result = find_peaks_stage.process(sample)

            assert isinstance(result, SAXSSample)
            np.testing.assert_array_equal(
                result.get_intensity_array(),
                intensity,
            )

    def test_find_peaks_stage_process_chain_calls(
        self,
        sample_data,
        find_peaks_stage,
    ) -> None:
        """Test FindAllPeaksStage with multiple consecutive calls."""
        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([4]),
                {"peak_heights": [30.0]},
            )

            result1 = find_peaks_stage.process(sample_data)
            result2 = find_peaks_stage.process(result1)
            result3 = find_peaks_stage.process(result2)

            # All results should have peaks in metadata
            assert "peaks" in result1.get_metadata_dict()
            assert "peaks" in result2.get_metadata_dict()
            assert "peaks" in result3.get_metadata_dict()

    def test_find_peaks_stage_with_suite(
        self,
        sample_data,
        find_peaks_chaining_stage,
    ) -> None:
        """Test FindAllPeaksStage with multiple consecutive calls."""
        with patch(
            "saxs.saxs.processing.stage.peak.find_peak_stage.find_peaks",
        ) as mock_find_peaks:
            mock_find_peaks.return_value = (
                np.array([4]),
                {"peak_heights": [30.0]},
            )

            sample1 = find_peaks_chaining_stage.process(sample_data)
            requests = find_peaks_chaining_stage.request_stage()
            logger.info(f"{requests}")
            # All results should have peaks in metadata
            assert "peaks" in sample1.get_metadata_dict()
            assert len(requests) > 0

            assert isinstance(requests[0].stage, AProcessPeakStage)
            new_stage = requests[0].stage
            sample2 = new_stage.process(sample1)
            logger.info(new_stage)
            logger.info(f"{sample2}")
            assert "peaks" in sample2.get_metadata_dict()

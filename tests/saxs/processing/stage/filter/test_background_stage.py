# Created by Isai Gordeev on 20/09/2025.

"""Tests for background_stage.py module."""

from unittest.mock import Mock, patch

import numpy as np
import pytest
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import (
    SampleMetadata,
    Intensity,
    IntensityError,
    QValues,
)
from saxs.saxs.processing.functions import background_hyberbole
from saxs.saxs.processing.stage.background.background import (
    BackgroundStage,
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    intensity = np.array([100.0, 80.0, 60.0, 45.0, 35.0])
    intensity_error = np.array([5.0, 4.0, 3.0, 2.5, 2.0])

    return SAXSSample(
        q_values=QValues(q_values),
        intensity=Intensity(intensity),
        intensity_error=IntensityError(intensity_error),
        metadata=SampleMetadata({"source": "test"}),
    )


@pytest.fixture
def background_stage():
    """Create BackgroundStage instance for testing."""
    return BackgroundStage()


class TestBackgroundStage:
    """Test cases for BackgroundStage class."""

    def test_background_stage_creation(self) -> None:
        """Test creating BackgroundStage with default parameters."""
        stage = BackgroundStage()

        assert hasattr(stage, "metadata")
        assert stage.metadata.value["_background_func"] == background_hyberbole
        assert "_background_coef" in stage.metadata.unwrap()

    def test_background_stage_creation_with_custom_function(self) -> None:
        """Test creating BackgroundStage with custom background function."""
        custom_func = Mock()
        stage = BackgroundStage(_background_func=custom_func)

        assert stage.metadata.value["_background_func"] == custom_func

    def test_background_stage_inheritance(self) -> None:
        """Test that BackgroundStage inherits from AbstractStage."""
        stage = BackgroundStage()
        from saxs.saxs.core.stage.abstract_stage import IAbstractStage

        assert isinstance(stage, IAbstractStage)

    def test_background_stage_metadata_structure(
        self,
        background_stage,
    ) -> None:
        """Test BackgroundStage metadata structure."""
        values = background_stage.metadata.unwrap()

        assert isinstance(values, dict)
        assert "_background_func" in values
        assert "_background_coef" in values
        assert callable(values["_background_func"])

    @patch("saxs.saxs.processing.stage.filter.background_stage.curve_fit")
    def test_background_stage_process_basic(
        self,
        mock_curve_fit,
        sample_data,
        background_stage,
    ) -> None:
        """Test BackgroundStage process method with basic functionality."""
        # Mock curve_fit to return known parameters
        mock_curve_fit.return_value = (
            np.array([2.0, 1.5]),
            np.array([[0.1, 0.0], [0.0, 0.1]]),
        )

        result = background_stage.process(sample_data)

        # Should return a SAXSSample
        assert isinstance(result, SAXSSample)
        assert result is not sample_data  # Should be a new instance

        # Should have called curve_fit
        mock_curve_fit.assert_called_once()

        # Check that curve_fit was called with correct arguments
        call_args = mock_curve_fit.call_args
        assert call_args[1]["f"] == background_hyberbole
        np.testing.assert_array_equal(
            call_args[1]["xdata"],
            sample_data.get_q_values_array(),
        )
        np.testing.assert_array_equal(
            call_args[1]["ydata"],
            sample_data.get_intensity_array(),
        )

    @patch("saxs.saxs.processing.stage.filter.background_stage.curve_fit")
    def test_background_stage_process_with_error_handling(
        self,
        mock_curve_fit,
        sample_data,
        background_stage,
    ) -> None:
        """Test BackgroundStage process method with curve_fit errors."""
        # Mock curve_fit to raise an exception
        mock_curve_fit.side_effect = RuntimeError("Fitting failed")

        with pytest.raises(RuntimeError, match="Fitting failed"):
            background_stage.process(sample_data)

    def test_background_stage_process_intensity_modification(
        self,
        sample_data,
        background_stage,
    ) -> None:
        """Test that BackgroundStage modifies intensity correctly."""
        original_intensity = sample_data.get_intensity_array()
        result = background_stage.process(sample_data)

        # The result should have modified intensity
        result_intensity = result.get_intensity_array()

        # Should be different (background subtracted)
        assert not np.array_equal(original_intensity, result_intensity)

        # Should have same length
        assert len(result_intensity) == len(original_intensity)

    @patch("saxs.saxs.processing.stage.filter.background_stage.curve_fit")
    def test_background_stage_process_preserves_other_data(
        self,
        mock_curve_fit,
        sample_data,
        background_stage,
    ) -> None:
        """Test that BackgroundStage preserves other sample data."""
        # Mock curve_fit to return known parameters
        mock_curve_fit.return_value = (
            np.array([2.0, 1.5]),
            np.array([[0.1, 0.0], [0.0, 0.1]]),
        )

        result = background_stage.process(sample_data)

        # Q values should be preserved
        np.testing.assert_array_equal(
            result.get_q_values_array(),
            sample_data.get_q_values_array(),
        )

        # Intensity error should be preserved
        np.testing.assert_array_equal(
            result.get_intensity_error_array(),
            sample_data.get_intensity_error_array(),
        )

        # Metadata should be preserved
        assert result.get_metadata_dict() == sample_data.get_metadata_dict()

    @patch("saxs.saxs.processing.stage.filter.background_stage.curve_fit")
    def test_background_stage_process_with_different_parameters(
        self,
        mock_curve_fit,
        sample_data,
    ) -> None:
        """Test BackgroundStage with different curve_fit parameters."""
        # Mock curve_fit to return different parameters
        mock_curve_fit.return_value = (
            np.array([1.0, 2.0]),
            np.array([[0.2, 0.0], [0.0, 0.2]]),
        )

        stage = BackgroundStage()
        result = stage.process(sample_data)

        # Should still work with different parameters
        assert isinstance(result, SAXSSample)
        mock_curve_fit.assert_called_once()

    def test_background_stage_process_with_minimal_data(self) -> None:
        """Test BackgroundStage with minimal sample data."""
        q_values = np.array([0.1, 0.2])
        intensity = np.array([10.0, 8.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
        )

        stage = BackgroundStage()

        with patch(
            "saxs.saxs.processing.stage.filter.background_stage.curve_fit",
        ) as mock_curve_fit:
            mock_curve_fit.return_value = (
                np.array([1.0, 1.0]),
                np.array([[0.1, 0.0], [0.0, 0.1]]),
            )

            result = stage.process(sample)

            assert isinstance(result, SAXSSample)
            assert len(result.get_q_values_array()) == 2
            assert len(result.get_intensity_array()) == 2

    def test_background_stage_process_with_none_error(self) -> None:
        """Test BackgroundStage with sample that has None intensity error."""
        q_values = np.array([0.1, 0.2, 0.3])
        intensity = np.array([10.0, 8.0, 6.0])

        sample = SAXSSample(
            q_values=QValues(q_values),
            intensity=Intensity(intensity),
            intensity_error=None,
        )

        stage = BackgroundStage()

        with patch(
            "saxs.saxs.processing.stage.filter.background_stage.curve_fit",
        ) as mock_curve_fit:
            mock_curve_fit.return_value = (
                np.array([1.0, 1.0]),
                np.array([[0.1, 0.0], [0.0, 0.1]]),
            )

            result = stage.process(sample)

            assert isinstance(result, SAXSSample)
            # Should handle None intensity error gracefully
            mock_curve_fit.assert_called_once()

    @patch("saxs.saxs.processing.stage.filter.background_stage.curve_fit")
    def test_background_stage_process_curve_fit_parameters(
        self,
        mock_curve_fit,
        sample_data,
        background_stage,
    ) -> None:
        """Test that curve_fit is called with correct parameters."""
        mock_curve_fit.return_value = (
            np.array([2.0, 1.5]),
            np.array([[0.1, 0.0], [0.0, 0.1]]),
        )

        background_stage.process(sample_data)

        # Check curve_fit call arguments
        call_args = mock_curve_fit.call_args
        assert call_args[1]["f"] == background_hyberbole
        assert call_args[1]["p0"] == (3, 2)  # Default initial parameters
        assert (
            call_args[1]["sigma"] is not None
        )  # Should use intensity error as sigma

    def test_background_stage_process_with_custom_background_function(
        self,
        sample_data,
    ) -> None:
        """Test BackgroundStage with custom background function."""
        custom_func = Mock()
        custom_func.return_value = np.array([1.0, 1.0, 1.0, 1.0, 1.0])

        stage = BackgroundStage(_background_func=custom_func)

        with patch(
            "saxs.saxs.processing.stage.filter.background_stage.curve_fit",
        ) as mock_curve_fit:
            mock_curve_fit.return_value = (
                np.array([1.0, 1.0]),
                np.array([[0.1, 0.0], [0.0, 0.1]]),
            )

            result = stage.process(sample_data)

            assert isinstance(result, SAXSSample)
            # Should use custom function
            call_args = mock_curve_fit.call_args
            assert call_args[1]["f"] == custom_func

    def test_background_stage_process_metadata_access(
        self,
        sample_data,
        background_stage,
    ) -> None:
        """Test that BackgroundStage accesses metadata correctly."""
        with patch(
            "saxs.saxs.processing.stage.filter.background_stage.curve_fit",
        ) as mock_curve_fit:
            mock_curve_fit.return_value = (
                np.array([2.0, 1.5]),
                np.array([[0.1, 0.0], [0.0, 0.1]]),
            )

            # Mock the metadata.get method
            result = background_stage.process(sample_data)
            assert isinstance(result, SAXSSample)

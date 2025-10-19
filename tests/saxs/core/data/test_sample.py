#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for sample.py module.
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import (
    Intensity,
    IntensityError,
    QValues,
)


class TestSAXSSample:
    """Test cases for SAXSSample class."""

    def test_saxs_sample_creation_minimal(self, q_values, intensity):
        """Test creating SAXSSample with minimal required fields."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        assert sample.q_values == q_values
        assert sample.intensity == intensity
        assert sample.intensity_error is None
        assert sample.metadata.unwrap() == {}

    def test_saxs_sample_creation_complete(
        self, q_values, intensity, intensity_error, metadata
    ):
        """Test creating SAXSSample with all fields."""
        sample = SAXSSample(
            q_values=q_values,
            intensity=intensity,
            intensity_error=intensity_error,
            metadata=metadata,
        )

        assert sample.q_values == q_values
        assert sample.intensity == intensity
        assert sample.intensity_error == intensity_error
        assert sample.metadata == metadata

    def test_saxs_sample_immutable(self, q_values, intensity):
        """Test that SAXSSample is immutable."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        with pytest.raises(FrozenInstanceError):
            sample.q_values = QValues(np.array([1, 2, 3]))

    def test_saxs_sample_getters(self, saxs_sample):
        """Test all getter methods."""
        sample = saxs_sample

        # Test basic getters
        assert sample.get_q_values() == sample.q_values
        assert sample.get_intensity() == sample.intensity
        assert sample.get_intensity_error() == sample.intensity_error
        assert sample.get_metadata() == sample.metadata

    def test_saxs_sample_array_getters(self, saxs_sample):
        """Test array unwrap getter methods."""
        sample = saxs_sample

        # Test array getters
        q_array = sample.get_q_values_array()
        intensity_array = sample.get_intensity_array()
        error_array = sample.get_intensity_error_array()
        metadata_dict = sample.get_metadata_dict()

        np.testing.assert_array_equal(q_array, sample.q_values.unwrap())
        np.testing.assert_array_equal(
            intensity_array, sample.intensity.unwrap()
        )
        np.testing.assert_array_equal(
            error_array, sample.intensity_error.unwrap()
        )
        assert metadata_dict == sample.metadata.unwrap()

    def test_saxs_sample_array_getters_with_none_error(
        self, q_values, intensity
    ):
        """Test array getters when intensity_error is None."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        q_array = sample.get_q_values_array()
        intensity_array = sample.get_intensity_array()
        error_array = sample.get_intensity_error_array()
        metadata_dict = sample.get_metadata_dict()

        np.testing.assert_array_equal(q_array, sample.get_q_values().unwrap())
        np.testing.assert_array_equal(
            intensity_array, sample.get_intensity().unwrap()
        )
        assert error_array is None
        assert metadata_dict == {}

    def test_saxs_sample_setters(self, q_values, intensity):
        """Test setter methods return new instances."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        # Test set_q_values
        new_q = np.array([0.5, 0.6, 0.7, 0.8, 0.9])
        new_sample = sample.set_q_values(new_q)

        assert new_sample is not sample  # Different instance
        np.testing.assert_array_equal(new_sample.get_q_values_array(), new_q)
        # assert sample.get_q_values_array() != new_q  # Original unchanged

        # Test set_intensity
        new_intensity = np.array([300.0, 400.0, 500.0, 600.0, 700.0])
        new_sample2 = sample.set_intensity(new_intensity)

        assert new_sample2 is not sample  # Different instance
        np.testing.assert_array_equal(
            new_sample2.get_intensity_array(), new_intensity
        )
        assert not np.array_equal(
            sample.get_intensity_array(), new_intensity
        )  # Original unchanged

        # Test set_intensity_error
        new_error = np.array([15.0, 20.0, 25.0, 30.0, 35.0])
        new_sample3 = sample.set_intensity_error(new_error)

        assert new_sample3 is not sample  # Different instance
        np.testing.assert_array_equal(
            new_sample3.get_intensity_error_array(), new_error
        )
        assert sample.get_intensity_error() is None  # Original unchanged

    def test_saxs_sample_set_intensity_error_none(self, saxs_sample):
        """Test setting intensity_error to None."""
        new_sample = saxs_sample.set_intensity_error(None)

        assert new_sample is not saxs_sample
        assert new_sample.get_intensity_error() is None

    def test_saxs_sample_chaining_setters(self, q_values, intensity):
        """Test chaining setter methods."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        new_q = np.array([0.5, 0.6, 0.7])
        new_intensity = np.array([300.0, 400.0, 500.0])
        new_error = np.array([15.0, 20.0, 25.0])

        # Chain multiple setters
        new_sample = (
            sample.set_q_values(new_q)
            .set_intensity(new_intensity)
            .set_intensity_error(new_error)
        )

        np.testing.assert_array_equal(new_sample.get_q_values_array(), new_q)
        np.testing.assert_array_equal(
            new_sample.get_intensity_array(), new_intensity
        )
        np.testing.assert_array_equal(
            new_sample.get_intensity_error_array(), new_error
        )

    def test_saxs_sample_with_different_array_sizes(self):
        """Test SAXSSample with different array sizes."""
        q_data = np.array([0.1, 0.2, 0.3])
        intensity_data = np.array([100.0, 200.0, 300.0])
        error_data = np.array([5.0, 10.0, 15.0])

        sample = SAXSSample(
            q_values=QValues(q_data),
            intensity=Intensity(intensity_data),
            intensity_error=IntensityError(error_data),
        )

        assert len(sample.get_q_values_array()) == 3
        assert len(sample.get_intensity_array()) == 3
        assert len(sample.get_intensity_error_array()) == 3

    def test_saxs_sample_with_empty_arrays(self):
        """Test SAXSSample with empty arrays."""
        q_data = np.array([])
        intensity_data = np.array([])

        sample = SAXSSample(
            q_values=QValues(q_data), intensity=Intensity(intensity_data)
        )

        assert len(sample.get_q_values_array()) == 0
        assert len(sample.get_intensity_array()) == 0

    def test_saxs_sample_equality(self, q_values, intensity):
        """Test SAXSSample equality comparison."""
        sample1 = SAXSSample(q_values=q_values, intensity=intensity)
        sample2 = SAXSSample(q_values=q_values, intensity=intensity)

        # Same data should be equal
        assert sample1 == sample2

        # Different data should not be equal
        different_q = QValues(np.array([1.0, 2.0, 3.0]))
        sample3 = SAXSSample(q_values=different_q, intensity=intensity)

        assert sample1 != sample3

    def test_saxs_sample_describe(self, q_values, intensity):
        """Test SAXSSample describe method from AData."""
        sample = SAXSSample(q_values=q_values, intensity=intensity)

        # Should have describe method (inherited from AData)
        assert hasattr(sample, "describe")
        assert callable(sample.describe)

        # Should return a string
        description = sample.describe()
        assert isinstance(description, str)
        assert len(description) > 0

#
# Created by Isai GORDEEV on 20/09/2025.
#


"""
Tests for sample_objects.py module.
"""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from saxs.saxs.core.data.sample_objects import (
    AbstractSampleMetadata,
    BaseDataType,
    Intensity,
    IntensityError,
    QValues,
)


class TestBaseArrayWrapper:
    """Test cases for BaseArrayWrapper class."""

    def test_base_array_wrapper_creation(self):
        """Test creating BaseArrayWrapper with and without values."""
        # With values
        wrapper = BaseDataType(values=np.array([1, 2, 3]))
        assert wrapper.values is not None
        np.testing.assert_array_equal(wrapper.values, np.array([1, 2, 3]))

        # Without values
        wrapper_empty = BaseDataType()
        assert wrapper_empty.values is None

    def test_base_array_wrapper_unwrap(self):
        """Test the unwrap method."""
        values = np.array([1, 2, 3, 4, 5])
        wrapper = BaseDataType(values=values)

        unwrapped = wrapper.unwrap()
        assert unwrapped is not None
        np.testing.assert_array_equal(unwrapped, values)

        # Test with None values
        wrapper_empty = BaseDataType()
        assert wrapper_empty.unwrap() is None

    def test_base_array_wrapper_immutable(self):
        """Test that BaseArrayWrapper is immutable."""
        wrapper = BaseDataType(values=np.array([1, 2, 3]))

        with pytest.raises(FrozenInstanceError):
            wrapper.values = np.array([4, 5, 6])


class TestQValues:
    """Test cases for QValues class."""

    def test_q_values_creation(self):
        """Test creating QValues with valid data."""
        q_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        q_values = QValues(values=q_data)

        assert q_values.values is not None
        np.testing.assert_array_equal(q_values.values, q_data)

    # def test_q_values_required_values(self):
    #     """Test that QValues requires values parameter."""
    #     with pytest.raises(TypeError):
    #         QValues()  # Missing required values parameter

    def test_q_values_unwrap(self):
        """Test QValues unwrap method."""
        q_data = np.array([0.1, 0.2, 0.3])
        q_values = QValues(values=q_data)

        unwrapped = q_values.unwrap()
        np.testing.assert_array_equal(unwrapped, q_data)

    def test_q_values_immutable(self):
        """Test that QValues is immutable."""
        q_values = QValues(values=np.array([1, 2, 3]))

        with pytest.raises(FrozenInstanceError):
            q_values.values = np.array([4, 5, 6])

    def test_q_values_with_different_dtypes(self):
        """Test QValues with different numpy dtypes."""
        # Float32
        q_float32 = QValues(values=np.array([0.1, 0.2], dtype=np.float32))
        assert q_float32.values.dtype == np.float32

        # Float64
        q_float64 = QValues(values=np.array([0.1, 0.2], dtype=np.float64))
        assert q_float64.values.dtype == np.float64


class TestIntensity:
    """Test cases for Intensity class."""

    def test_intensity_creation(self):
        """Test creating Intensity with valid data."""
        intensity_data = np.array([100.0, 150.0, 200.0])
        intensity = Intensity(values=intensity_data)

        assert intensity.values is not None
        np.testing.assert_array_equal(intensity.values, intensity_data)

    # def test_intensity_required_values(self):
    #     """Test that Intensity requires values parameter."""
    #     with pytest.raises(TypeError):
    #         Intensity()  # Missing required values parameter

    def test_intensity_unwrap(self):
        """Test Intensity unwrap method."""
        intensity_data = np.array([100.0, 150.0, 200.0])
        intensity = Intensity(values=intensity_data)

        unwrapped = intensity.unwrap()
        np.testing.assert_array_equal(unwrapped, intensity_data)

    def test_intensity_immutable(self):
        """Test that Intensity is immutable."""
        intensity = Intensity(values=np.array([100, 200]))

        with pytest.raises(FrozenInstanceError):
            intensity.values = np.array([300, 400])

    def test_intensity_with_negative_values(self):
        """Test Intensity with negative values (should be allowed)."""
        intensity_data = np.array([-10.0, 0.0, 100.0])
        intensity = Intensity(values=intensity_data)
        np.testing.assert_array_equal(intensity.values, intensity_data)


class TestIntensityError:
    """Test cases for IntensityError class."""

    def test_intensity_error_creation_with_values(self):
        """Test creating IntensityError with values."""
        error_data = np.array([5.0, 7.5, 10.0])
        intensity_error = IntensityError(values=error_data)

        assert intensity_error.values is not None
        np.testing.assert_array_equal(intensity_error.values, error_data)

    def test_intensity_error_creation_without_values(self):
        """Test creating IntensityError without values (should be None)."""
        intensity_error = IntensityError()
        assert intensity_error.values is None

    def test_intensity_error_unwrap(self):
        """Test IntensityError unwrap method."""
        # With values
        error_data = np.array([5.0, 7.5, 10.0])
        intensity_error = IntensityError(values=error_data)
        unwrapped = intensity_error.unwrap()
        np.testing.assert_array_equal(unwrapped, error_data)

        # Without values
        intensity_error_empty = IntensityError()
        assert intensity_error_empty.unwrap() is None

    def test_intensity_error_immutable(self):
        """Test that IntensityError is immutable."""
        intensity_error = IntensityError(values=np.array([1, 2]))

        with pytest.raises(FrozenInstanceError):
            intensity_error.values = np.array([3, 4])

    def test_intensity_error_with_zero_values(self):
        """Test IntensityError with zero values."""
        error_data = np.array([0.0, 0.0, 0.0])
        intensity_error = IntensityError(values=error_data)
        np.testing.assert_array_equal(intensity_error.values, error_data)


class TestAbstractSampleMetadata:
    """Test cases for AbstractSampleMetadata class."""

    def test_metadata_creation_with_dict(self):
        """Test creating AbstractSampleMetadata with dictionary."""
        metadata_dict = {"temperature": 25.0, "pressure": 1.0}
        metadata = AbstractSampleMetadata(values=metadata_dict)

        assert metadata.values == metadata_dict
        assert len(metadata.values) == 2

    def test_metadata_creation_empty(self):
        """Test creating AbstractSampleMetadata with empty dictionary."""
        metadata = AbstractSampleMetadata()
        assert metadata.values == {}
        assert len(metadata.values) == 0

    def test_metadata_creation_with_nested_dict(self):
        """Test creating AbstractSampleMetadata with nested dictionary."""
        nested_dict = {
            "experiment": {"temperature": 25.0, "pressure": 1.0},
            "sample": {"id": "test_001", "type": "protein"},
        }
        metadata = AbstractSampleMetadata(values=nested_dict)
        assert metadata.values == nested_dict

    def test_metadata_unwrap(self):
        """Test AbstractSampleMetadata unwrap method."""
        metadata_dict = {"key1": "value1", "key2": 42}
        metadata = AbstractSampleMetadata(values=metadata_dict)

        unwrapped = metadata.unwrap()
        assert unwrapped == metadata_dict

    def test_metadata_immutable(self):
        """Test that AbstractSampleMetadata is immutable."""
        metadata = AbstractSampleMetadata(values={"key": "value"})

        with pytest.raises(FrozenInstanceError):
            metadata.values = {"new_key": "new_value"}

    def test_metadata_with_various_types(self):
        """Test AbstractSampleMetadata with various value types."""
        complex_dict = {
            "string": "test",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "nested_dict": {"inner": "value"},
            "none": None,
        }
        metadata = AbstractSampleMetadata(values=complex_dict)
        assert metadata.values == complex_dict

    def test_metadata_inheritance(self):
        """Test that AbstractSampleMetadata inherits from BaseArrayWrapper."""
        metadata = AbstractSampleMetadata(values={"key": "value"})
        assert isinstance(metadata, BaseDataType)

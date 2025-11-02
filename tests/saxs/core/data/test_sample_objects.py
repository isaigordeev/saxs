# Created by Isai Gordeev on 20/09/2025.

"""Tests for sample_objects.py module."""

from dataclasses import FrozenInstanceError

import numpy as np
import pytest
from saxs.saxs.core.types.abstract_data import TBaseDataType
from saxs.saxs.core.types.sample_objects import (
    AbstractSampleMetadata,
    Intensity,
    IntensityError,
    QValues,
)


class TestBaseArrayWrapper:
    """Test cases for BaseArrayWrapper class."""

    def test_base_array_wrapper_creation(self) -> None:
        """Test creating BaseArrayWrapper with and without values."""
        # With values
        wrapper = TBaseDataType(value=np.array([1, 2, 3]))
        assert wrapper.value is not None
        np.testing.assert_array_equal(wrapper.value, np.array([1, 2, 3]))

        # Without values
        wrapper_empty = TBaseDataType()
        assert wrapper_empty.value is None

    def test_base_array_wrapper_unwrap(self) -> None:
        """Test the unwrap method."""
        values = np.array([1, 2, 3, 4, 5])
        wrapper = TBaseDataType(value=values)

        unwrapped = wrapper.unwrap()
        assert unwrapped is not None
        np.testing.assert_array_equal(unwrapped, values)

        # Test with None values
        wrapper_empty = TBaseDataType()
        assert wrapper_empty.unwrap() is None

    def test_base_array_wrapper_immutable(self) -> None:
        """Test that BaseArrayWrapper is immutable."""
        wrapper = TBaseDataType(value=np.array([1, 2, 3]))

        with pytest.raises(FrozenInstanceError):
            wrapper.value = np.array([4, 5, 6])


class TestQValues:
    """Test cases for QValues class."""

    def test_q_values_creation(self) -> None:
        """Test creating QValues with valid data."""
        q_data = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        q_values = QValues(value=q_data)

        assert q_values.value is not None
        np.testing.assert_array_equal(q_values.value, q_data)

    # def test_q_values_required_values(self):
    #     """Test that QValues requires values parameter."""
    #     with pytest.raises(TypeError):
    #         QValues()  # Missing required values parameter

    def test_q_values_unwrap(self) -> None:
        """Test QValues unwrap method."""
        q_data = np.array([0.1, 0.2, 0.3])
        q_values = QValues(value=q_data)

        unwrapped = q_values.unwrap()
        np.testing.assert_array_equal(unwrapped, q_data)

    def test_q_values_immutable(self) -> None:
        """Test that QValues is immutable."""
        q_values = QValues(value=np.array([1, 2, 3]))

        with pytest.raises(FrozenInstanceError):
            q_values.value = np.array([4, 5, 6])

    def test_q_values_with_different_dtypes(self) -> None:
        """Test QValues with different numpy dtypes."""
        # Float32
        q_float32 = QValues(value=np.array([0.1, 0.2], dtype=np.float32))
        assert q_float32.value.dtype == np.float32

        # Float64
        q_float64 = QValues(value=np.array([0.1, 0.2], dtype=np.float64))
        assert q_float64.value.dtype == np.float64


class TestIntensity:
    """Test cases for Intensity class."""

    def test_intensity_creation(self) -> None:
        """Test creating Intensity with valid data."""
        intensity_data = np.array([100.0, 150.0, 200.0])
        intensity = Intensity(value=intensity_data)

        assert intensity.value is not None
        np.testing.assert_array_equal(intensity.value, intensity_data)

    # def test_intensity_required_values(self):
    #     """Test that Intensity requires values parameter."""
    #     with pytest.raises(TypeError):
    #         Intensity()  # Missing required values parameter

    def test_intensity_unwrap(self) -> None:
        """Test Intensity unwrap method."""
        intensity_data = np.array([100.0, 150.0, 200.0])
        intensity = Intensity(value=intensity_data)

        unwrapped = intensity.unwrap()
        np.testing.assert_array_equal(unwrapped, intensity_data)

    def test_intensity_immutable(self) -> None:
        """Test that Intensity is immutable."""
        intensity = Intensity(value=np.array([100, 200]))

        with pytest.raises(FrozenInstanceError):
            intensity.value = np.array([300, 400])

    def test_intensity_with_negative_values(self) -> None:
        """Test Intensity with negative values (should be allowed)."""
        intensity_data = np.array([-10.0, 0.0, 100.0])
        intensity = Intensity(value=intensity_data)
        np.testing.assert_array_equal(intensity.value, intensity_data)


class TestIntensityError:
    """Test cases for IntensityError class."""

    def test_intensity_error_creation_with_values(self) -> None:
        """Test creating IntensityError with values."""
        error_data = np.array([5.0, 7.5, 10.0])
        intensity_error = IntensityError(value=error_data)

        assert intensity_error.value is not None
        np.testing.assert_array_equal(intensity_error.value, error_data)

    def test_intensity_error_creation_without_values(self) -> None:
        """Test creating IntensityError without values (should be None)."""
        intensity_error = IntensityError()
        assert intensity_error.value is None

    def test_intensity_error_unwrap(self) -> None:
        """Test IntensityError unwrap method."""
        # With values
        error_data = np.array([5.0, 7.5, 10.0])
        intensity_error = IntensityError(value=error_data)
        unwrapped = intensity_error.unwrap()
        np.testing.assert_array_equal(unwrapped, error_data)

        # Without values
        intensity_error_empty = IntensityError()
        assert intensity_error_empty.unwrap() is None

    def test_intensity_error_immutable(self) -> None:
        """Test that IntensityError is immutable."""
        intensity_error = IntensityError(value=np.array([1, 2]))

        with pytest.raises(FrozenInstanceError):
            intensity_error.value = np.array([3, 4])

    def test_intensity_error_with_zero_values(self) -> None:
        """Test IntensityError with zero values."""
        error_data = np.array([0.0, 0.0, 0.0])
        intensity_error = IntensityError(value=error_data)
        np.testing.assert_array_equal(intensity_error.value, error_data)


class TestAbstractSampleMetadata:
    """Test cases for AbstractSampleMetadata class."""

    def test_metadata_creation_with_dict(self) -> None:
        """Test creating AbstractSampleMetadata with dictionary."""
        metadata_dict = {"temperature": 25.0, "pressure": 1.0}
        metadata = AbstractSampleMetadata(value=metadata_dict)

        assert metadata.value == metadata_dict
        assert len(metadata.value) == 2

    def test_metadata_creation_empty(self) -> None:
        """Test creating AbstractSampleMetadata with empty dictionary."""
        metadata = AbstractSampleMetadata()
        assert metadata.value == {}
        assert len(metadata.value) == 0

    def test_metadata_creation_with_nested_dict(self) -> None:
        """Test creating AbstractSampleMetadata with nested dictionary."""
        nested_dict = {
            "experiment": {"temperature": 25.0, "pressure": 1.0},
            "sample": {"id": "test_001", "type": "protein"},
        }
        metadata = AbstractSampleMetadata(value=nested_dict)
        assert metadata.value == nested_dict

    def test_metadata_unwrap(self) -> None:
        """Test AbstractSampleMetadata unwrap method."""
        metadata_dict = {"key1": "value1", "key2": 42}
        metadata = AbstractSampleMetadata(value=metadata_dict)

        unwrapped = metadata.unwrap()
        assert unwrapped == metadata_dict

    def test_metadata_immutable(self) -> None:
        """Test that AbstractSampleMetadata is immutable."""
        metadata = AbstractSampleMetadata(value={"key": "value"})

        with pytest.raises(FrozenInstanceError):
            metadata.value = {"new_key": "new_value"}

    def test_metadata_with_various_types(self) -> None:
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
        metadata = AbstractSampleMetadata(value=complex_dict)
        assert metadata.value == complex_dict

    def test_metadata_inheritance(self) -> None:
        """Test that AbstractSampleMetadata inherits from BaseArrayWrapper."""
        metadata = AbstractSampleMetadata(value={"key": "value"})
        assert isinstance(metadata, TBaseDataType)

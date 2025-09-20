# #
# # Created by Isai GORDEEV on 20/09/2025.
# #

# """
# Tests for filter_stage.py module.
# """

# import numpy as np
# import pytest

# from saxs.saxs.core.data.sample import SAXSSample
# from saxs.saxs.core.data.sample_objects import (
#     AbstractSampleMetadata,
#     Intensity,
#     IntensityError,
#     QValues,
# )
# from saxs.saxs.processing.stage.filter.filter_stage import FilterStage


# @pytest.fixture
# def sample_data():
#     """Create sample data for testing."""
#     q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
#     intensity = np.array([100.0, 80.0, 60.0, 45.0, 35.0])
#     intensity_error = np.array([5.0, 4.0, 3.0, 2.5, 2.0])

#     return SAXSSample(
#         q_values=QValues(q_values),
#         intensity=Intensity(intensity),
#         intensity_error=IntensityError(intensity_error),
#         metadata=AbstractSampleMetadata({"source": "test"})
#     )


# @pytest.fixture
# def filter_stage():
#     """Create FilterStage instance for testing."""
#     return FilterStage()


# class TestFilterStage:
#     """Test cases for FilterStage class."""

#     def test_filter_stage_creation(self):
#         """Test creating FilterStage."""
#         stage = FilterStage()

#         assert hasattr(stage, 'metadata')
#         # FilterStage doesn't set metadata in __init__, so it should be None or default
#         # This depends on the AbstractStage implementation

#     def test_filter_stage_inheritance(self):
#         """Test that FilterStage inherits from AbstractStage."""
#         stage = FilterStage()
#         from saxs.saxs.core.stage.abstract_stage import AbstractStage
#         assert isinstance(stage, AbstractStage)

#     def test_filter_stage_process_method(self, sample_data, filter_stage):
#         """Test FilterStage process method."""
#         result = filter_stage.process(sample_data)

#         # Should return a SAXSSample
#         assert isinstance(result, SAXSSample)

#         # Since FilterStage just calls super().process(), it should return the same data
#         # This depends on the AbstractStage implementation
#         assert result == sample_data

#     def test_filter_stage_process_preserves_data(self, sample_data, filter_stage):
#         """Test that FilterStage preserves all sample data."""
#         result = filter_stage.process(sample_data)

#         # All data should be preserved
#         np.testing.assert_array_equal(result.get_q_values_array(), sample_data.get_q_values_array())
#         np.testing.assert_array_equal(result.get_intensity_array(), sample_data.get_intensity_array())
#         np.testing.assert_array_equal(result.get_intensity_error_array(), sample_data.get_intensity_error_array())
#         assert result.get_metadata_dict() == sample_data.get_metadata_dict()

#     def test_filter_stage_process_immutability(self, sample_data, filter_stage):
#         """Test that FilterStage doesn't modify the original sample."""
#         original_q = sample_data.get_q_values_array().copy()
#         original_i = sample_data.get_intensity_array().copy()
#         original_e = sample_data.get_intensity_error_array().copy()
#         original_meta = sample_data.get_metadata_dict().copy()

#         result = filter_stage.process(sample_data)

#         # Original sample should be unchanged
#         np.testing.assert_array_equal(sample_data.get_q_values_array(), original_q)
#         np.testing.assert_array_equal(sample_data.get_intensity_array(), original_i)
#         np.testing.assert_array_equal(sample_data.get_intensity_error_array(), original_e)
#         assert sample_data.get_metadata_dict() == original_meta

#     def test_filter_stage_process_with_different_samples(self, filter_stage):
#         """Test FilterStage with different sample types."""
#         # Test with minimal sample
#         q_values = np.array([0.1, 0.2])
#         intensity = np.array([10.0, 8.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result == sample

#     def test_filter_stage_process_with_none_error(self, filter_stage):
#         """Test FilterStage with sample that has None intensity error."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, 8.0, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             intensity_error=None
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_intensity_error() is None

#     def test_filter_stage_process_consistency(self, sample_data, filter_stage):
#         """Test that FilterStage produces consistent results."""
#         result1 = filter_stage.process(sample_data)
#         result2 = filter_stage.process(sample_data)

#         # Should produce identical results
#         assert result1 == result2

#     def test_filter_stage_process_with_empty_data(self, filter_stage):
#         """Test FilterStage with empty sample data."""
#         sample = SAXSSample(
#             q_values=QValues(np.array([])),
#             intensity=Intensity(np.array([]))
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 0
#         assert len(result.get_intensity_array()) == 0

#     def test_filter_stage_process_with_metadata(self, filter_stage):
#         """Test FilterStage with sample containing metadata."""
#         q_values = np.array([0.1, 0.2])
#         intensity = np.array([10.0, 8.0])
#         metadata = AbstractSampleMetadata({"test_key": "test_value", "number": 42})

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_metadata_dict() == sample.get_metadata_dict()

#     def test_filter_stage_process_returns_new_instance(self, sample_data, filter_stage):
#         """Test that FilterStage returns a new instance."""
#         result = filter_stage.process(sample_data)

#         # Should be a new instance (not the same object)
#         assert result is not sample_data

#         # But should have the same content
#         assert result == sample_data

#     def test_filter_stage_process_with_different_data_types(self, filter_stage):
#         """Test FilterStage with different data types."""
#         # Test with float32 data
#         q_values = np.array([0.1, 0.2, 0.3], dtype=np.float32)
#         intensity = np.array([10.0, 8.0, 6.0], dtype=np.float32)

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_q_values_array().dtype == np.float32
#         assert result.get_intensity_array().dtype == np.float32

#     def test_filter_stage_process_with_negative_values(self, filter_stage):
#         """Test FilterStage with negative intensity values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([-10.0, 0.0, 10.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_filter_stage_process_with_large_values(self, filter_stage):
#         """Test FilterStage with large values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([1e6, 2e6, 3e6])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_filter_stage_process_with_nan_values(self, filter_stage):
#         """Test FilterStage with NaN values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, np.nan, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity, equal_nan=True)

#     def test_filter_stage_process_with_inf_values(self, filter_stage):
#         """Test FilterStage with infinite values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, np.inf, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = filter_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_filter_stage_process_chain_calls(self, sample_data, filter_stage):
#         """Test FilterStage with multiple consecutive calls."""
#         result1 = filter_stage.process(sample_data)
#         result2 = filter_stage.process(result1)
#         result3 = filter_stage.process(result2)

#         # All results should be identical
#         assert result1 == result2
#         assert result2 == result3
#         assert result1 == sample_data

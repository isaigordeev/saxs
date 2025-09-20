# #
# # Created by Isai GORDEEV on 20/09/2025.
# #

# """
# Tests for process_peak_stage.py module.
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
# from saxs.saxs.processing.stage.peak.process_peak_stage import ProcessPeakStage


# @pytest.fixture
# def sample_data():
#     """Create sample data for testing."""
#     q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
#     intensity = np.array([10.0, 15.0, 20.0, 25.0, 30.0, 25.0, 20.0, 15.0, 10.0, 5.0])
#     intensity_error = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5])

#     return SAXSSample(
#         q_values=QValues(q_values),
#         intensity=Intensity(intensity),
#         intensity_error=IntensityError(intensity_error),
#         metadata=AbstractSampleMetadata({"source": "test", "peaks": np.array([4])})
#     )


# @pytest.fixture
# def process_peak_stage():
#     """Create ProcessPeakStage instance for testing."""
#     return ProcessPeakStage()


# class TestProcessPeakStage:
#     """Test cases for ProcessPeakStage class."""

#     def test_process_peak_stage_creation(self):
#         """Test creating ProcessPeakStage."""
#         stage = ProcessPeakStage()

#         # ProcessPeakStage is currently empty, so we just test that it can be created
#         assert stage is not None

#     def test_process_peak_stage_inheritance(self):
#         """Test that ProcessPeakStage inherits from AbstractSelfRepeatingConditionalStage."""
#         stage = ProcessPeakStage()
#         from saxs.saxs.core.stage.abstract_stage import AbstractSelfRepeatingConditionalStage
#         assert isinstance(stage, AbstractSelfRepeatingConditionalStage)

#     def test_process_peak_stage_has_required_methods(self, process_peak_stage):
#         """Test that ProcessPeakStage has required methods."""
#         # Check that it has the required methods from AbstractStage
#         assert hasattr(process_peak_stage, 'process')
#         assert hasattr(process_peak_stage, '_process')
#         assert hasattr(process_peak_stage, 'get_next_stage')

#         # Check that methods are callable
#         assert callable(process_peak_stage.process)
#         assert callable(process_peak_stage._process)
#         assert callable(process_peak_stage.get_next_stage)

#     def test_process_peak_stage_process_method(self, sample_data, process_peak_stage):
#         """Test ProcessPeakStage process method."""
#         result = process_peak_stage.process(sample_data)

#         # Should return a SAXSSample
#         assert isinstance(result, SAXSSample)

#         # Since ProcessPeakStage is currently empty, it should return the same data
#         # This depends on the AbstractSelfRepeatingConditionalStage implementation
#         assert result == sample_data

#     def test_process_peak_stage_process_preserves_data(self, sample_data, process_peak_stage):
#         """Test that ProcessPeakStage preserves all sample data."""
#         result = process_peak_stage.process(sample_data)

#         # All data should be preserved
#         np.testing.assert_array_equal(result.get_q_values_array(), sample_data.get_q_values_array())
#         np.testing.assert_array_equal(result.get_intensity_array(), sample_data.get_intensity_array())
#         np.testing.assert_array_equal(result.get_intensity_error_array(), sample_data.get_intensity_error_array())
#         assert result.get_metadata_dict() == sample_data.get_metadata_dict()

#     def test_process_peak_stage_process_immutability(self, sample_data, process_peak_stage):
#         """Test that ProcessPeakStage doesn't modify the original sample."""
#         original_q = sample_data.get_q_values_array().copy()
#         original_i = sample_data.get_intensity_array().copy()
#         original_e = sample_data.get_intensity_error_array().copy()
#         original_meta = sample_data.get_metadata_dict().copy()

#         result = process_peak_stage.process(sample_data)

#         # Original sample should be unchanged
#         np.testing.assert_array_equal(sample_data.get_q_values_array(), original_q)
#         np.testing.assert_array_equal(sample_data.get_intensity_array(), original_i)
#         np.testing.assert_array_equal(sample_data.get_intensity_error_array(), original_e)
#         assert sample_data.get_metadata_dict() == original_meta

#     def test_process_peak_stage_process_with_different_samples(self, process_peak_stage):
#         """Test ProcessPeakStage with different sample types."""
#         # Test with minimal sample
#         q_values = np.array([0.1, 0.2])
#         intensity = np.array([10.0, 8.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result == sample

#     def test_process_peak_stage_process_with_none_error(self, process_peak_stage):
#         """Test ProcessPeakStage with sample that has None intensity error."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, 8.0, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             intensity_error=None
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_intensity_error() is None

#     def test_process_peak_stage_process_consistency(self, sample_data, process_peak_stage):
#         """Test that ProcessPeakStage produces consistent results."""
#         result1 = process_peak_stage.process(sample_data)
#         result2 = process_peak_stage.process(sample_data)

#         # Should produce identical results
#         assert result1 == result2

#     def test_process_peak_stage_process_with_empty_data(self, process_peak_stage):
#         """Test ProcessPeakStage with empty sample data."""
#         sample = SAXSSample(
#             q_values=QValues(np.array([])),
#             intensity=Intensity(np.array([]))
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 0
#         assert len(result.get_intensity_array()) == 0

#     def test_process_peak_stage_process_with_metadata(self, process_peak_stage):
#         """Test ProcessPeakStage with sample containing metadata."""
#         q_values = np.array([0.1, 0.2])
#         intensity = np.array([10.0, 8.0])
#         metadata = AbstractSampleMetadata({"test_key": "test_value", "number": 42})

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_metadata_dict() == sample.get_metadata_dict()

#     def test_process_peak_stage_process_returns_new_instance(self, sample_data, process_peak_stage):
#         """Test that ProcessPeakStage returns a new instance."""
#         result = process_peak_stage.process(sample_data)

#         # Should be a new instance (not the same object)
#         assert result is not sample_data

#         # But should have the same content
#         assert result == sample_data

#     def test_process_peak_stage_process_with_different_data_types(self, process_peak_stage):
#         """Test ProcessPeakStage with different data types."""
#         # Test with float32 data
#         q_values = np.array([0.1, 0.2, 0.3], dtype=np.float32)
#         intensity = np.array([10.0, 8.0, 6.0], dtype=np.float32)

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_q_values_array().dtype == np.float32
#         assert result.get_intensity_array().dtype == np.float32

#     def test_process_peak_stage_process_with_negative_values(self, process_peak_stage):
#         """Test ProcessPeakStage with negative intensity values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([-10.0, 0.0, 10.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_process_peak_stage_process_with_large_values(self, process_peak_stage):
#         """Test ProcessPeakStage with large values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([1e6, 2e6, 3e6])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_process_peak_stage_process_with_nan_values(self, process_peak_stage):
#         """Test ProcessPeakStage with NaN values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, np.nan, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity, equal_nan=True)

#     def test_process_peak_stage_process_with_inf_values(self, process_peak_stage):
#         """Test ProcessPeakStage with infinite values."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, np.inf, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity)
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         np.testing.assert_array_equal(result.get_intensity_array(), intensity)

#     def test_process_peak_stage_process_chain_calls(self, sample_data, process_peak_stage):
#         """Test ProcessPeakStage with multiple consecutive calls."""
#         result1 = process_peak_stage.process(sample_data)
#         result2 = process_peak_stage.process(result1)
#         result3 = process_peak_stage.process(result2)

#         # All results should be identical
#         assert result1 == result2
#         assert result2 == result3
#         assert result1 == sample_data

#     def test_process_peak_stage_get_next_stage(self, process_peak_stage):
#         """Test ProcessPeakStage get_next_stage method."""
#         next_stages = process_peak_stage.get_next_stage()

#         # Should return a list (empty for now)
#         assert isinstance(next_stages, list)

#     def test_process_peak_stage_with_peaks_metadata(self, process_peak_stage):
#         """Test ProcessPeakStage with sample containing peaks metadata."""
#         q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
#         intensity = np.array([10.0, 15.0, 20.0, 15.0, 10.0])
#         metadata = AbstractSampleMetadata({"peaks": np.array([2]), "source": "test"})

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert "peaks" in result.get_metadata_dict()
#         assert result.get_metadata_dict()["peaks"].tolist() == [2]

#     def test_process_peak_stage_with_complex_metadata(self, process_peak_stage):
#         """Test ProcessPeakStage with complex metadata."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, 8.0, 6.0])
#         metadata = AbstractSampleMetadata({
#             "peaks": np.array([1]),
#             "peak_heights": [8.0],
#             "processing_stage": "peak_detection",
#             "parameters": {"threshold": 0.5, "method": "gaussian"}
#         })

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert result.get_metadata_dict() == sample.get_metadata_dict()

#     def test_process_peak_stage_with_empty_peaks(self, process_peak_stage):
#         """Test ProcessPeakStage with empty peaks metadata."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, 8.0, 6.0])
#         metadata = AbstractSampleMetadata({"peaks": np.array([]), "source": "test"})

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert "peaks" in result.get_metadata_dict()
#         assert len(result.get_metadata_dict()["peaks"]) == 0

#     def test_process_peak_stage_with_multiple_peaks(self, process_peak_stage):
#         """Test ProcessPeakStage with multiple peaks metadata."""
#         q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
#         intensity = np.array([10.0, 15.0, 20.0, 15.0, 10.0])
#         metadata = AbstractSampleMetadata({"peaks": np.array([1, 2, 3]), "source": "test"})

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             metadata=metadata
#         )

#         result = process_peak_stage.process(sample)
#         assert isinstance(result, SAXSSample)
#         assert "peaks" in result.get_metadata_dict()
#         assert len(result.get_metadata_dict()["peaks"]) == 3
#         np.testing.assert_array_equal(result.get_metadata_dict()["peaks"], np.array([1, 2, 3]))

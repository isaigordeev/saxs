# #
# # Created by Isai GORDEEV on 20/09/2025.
# #

# """
# Tests for cut_stage.py module.
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
# from saxs.saxs.processing.stage.filter.cut_stage import CutStage


# @pytest.fixture
# def sample_data():
#     """Create sample data for testing."""
#     q_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
#     intensity = np.array(
#         [100.0, 90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0, 10.0]
#     )
#     intensity_error = np.array(
#         [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5]
#     )

#     return SAXSSample(
#         q_values=QValues(q_values),
#         intensity=Intensity(intensity),
#         intensity_error=IntensityError(intensity_error),
#         metadata=AbstractSampleMetadata({"source": "test"}),
#     )


# @pytest.fixture
# def cut_stage():
#     """Create CutStage instance for testing."""
#     return CutStage(cut_point=5)


# class TestCutStage:
#     """Test cases for CutStage class."""

#     def test_cut_stage_creation_default(self):
#         """Test creating CutStage with default parameters."""
#         stage = CutStage()

#         assert hasattr(stage, "metadata")
#         assert stage.metadata.data["cut_point"] == 100

#     def test_cut_stage_creation_custom(self):
#         """Test creating CutStage with custom cut point."""
#         stage = CutStage(cut_point=50)

#         assert stage.metadata.data["cut_point"] == 50

#     def test_cut_stage_inheritance(self):
#         """Test that CutStage inherits from AbstractStage."""
#         stage = CutStage()
#         from saxs.saxs.core.stage.abstract_stage import AbstractStage

#         assert isinstance(stage, AbstractStage)

#     def test_cut_stage_metadata_structure(self, cut_stage):
#         """Test CutStage metadata structure."""
#         metadata = cut_stage.metadata

#         assert isinstance(metadata, AbstractSampleMetadata)
#         assert "cut_point" in metadata.data
#         assert isinstance(metadata.data["cut_point"], int)

#     def test_cut_stage_process_basic(self, sample_data, cut_stage):
#         """Test CutStage process method with basic functionality."""
#         result = cut_stage.process(sample_data)

#         # Should return a SAXSSample
#         assert isinstance(result, SAXSSample)
#         assert result is not sample_data  # Should be a new instance

#         # Should have cut the data at cut_point=5
#         assert len(result.get_q_values_array()) == 5
#         assert len(result.get_intensity_array()) == 5
#         assert len(result.get_intensity_error_array()) == 5

#     def test_cut_stage_process_correct_cutting(self, sample_data, cut_stage):
#         """Test that CutStage cuts the data correctly."""
#         result = cut_stage.process(sample_data)

#         # Check that the first 5 elements are preserved
#         original_q = sample_data.get_q_values_array()
#         original_i = sample_data.get_intensity_array()
#         original_e = sample_data.get_intensity_error_array()

#         result_q = result.get_q_values_array()
#         result_i = result.get_intensity_array()
#         result_e = result.get_intensity_error_array()

#         np.testing.assert_array_equal(result_q, original_q[:5])
#         np.testing.assert_array_equal(result_i, original_i[:5])
#         np.testing.assert_array_equal(result_e, original_e[:5])

#     def test_cut_stage_process_preserves_metadata(self, sample_data, cut_stage):
#         """Test that CutStage preserves sample metadata."""
#         result = cut_stage.process(sample_data)

#         # Metadata should be preserved
#         assert result.get_metadata_dict() == sample_data.get_metadata_dict()

#     def test_cut_stage_process_different_cut_points(self, sample_data):
#         """Test CutStage with different cut points."""
#         # Test with cut_point = 3
#         stage3 = CutStage(cut_point=3)
#         result3 = stage3.process(sample_data)
#         assert len(result3.get_q_values_array()) == 3

#         # Test with cut_point = 7
#         stage7 = CutStage(cut_point=7)
#         result7 = stage7.process(sample_data)
#         assert len(result7.get_q_values_array()) == 7

#         # Test with cut_point = 1
#         stage1 = CutStage(cut_point=1)
#         result1 = stage1.process(sample_data)
#         assert len(result1.get_q_values_array()) == 1

#     def test_cut_stage_process_cut_point_larger_than_data(self, sample_data):
#         """Test CutStage when cut_point is larger than data length."""
#         stage = CutStage(cut_point=20)  # Larger than data length (10)

#         result = stage.process(sample_data)

#         # Should return all data (no cutting)
#         assert len(result.get_q_values_array()) == len(
#             sample_data.get_q_values_array()
#         )
#         np.testing.assert_array_equal(
#             result.get_q_values_array(), sample_data.get_q_values_array()
#         )

#     def test_cut_stage_process_cut_point_zero(self, sample_data):
#         """Test CutStage with cut_point = 0."""
#         stage = CutStage(cut_point=0)

#         result = stage.process(sample_data)

#         # Should return empty arrays
#         assert len(result.get_q_values_array()) == 0
#         assert len(result.get_intensity_array()) == 0
#         assert len(result.get_intensity_error_array()) == 0

#     def test_cut_stage_process_negative_cut_point(self, sample_data):
#         """Test CutStage with negative cut_point."""
#         stage = CutStage(cut_point=-5)

#         # Should handle negative cut_point gracefully
#         result = stage.process(sample_data)

#         # Should return empty arrays or handle gracefully
#         assert isinstance(result, SAXSSample)

#     def test_cut_stage_process_with_minimal_data(self):
#         """Test CutStage with minimal sample data."""
#         q_values = np.array([0.1, 0.2])
#         intensity = np.array([10.0, 8.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values), intensity=Intensity(intensity)
#         )

#         stage = CutStage(cut_point=1)
#         result = stage.process(sample)

#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 1
#         assert len(result.get_intensity_array()) == 1

#     def test_cut_stage_process_with_none_error(self):
#         """Test CutStage with sample that has None intensity error."""
#         q_values = np.array([0.1, 0.2, 0.3])
#         intensity = np.array([10.0, 8.0, 6.0])

#         sample = SAXSSample(
#             q_values=QValues(q_values),
#             intensity=Intensity(intensity),
#             intensity_error=None,
#         )

#         stage = CutStage(cut_point=2)
#         result = stage.process(sample)

#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 2
#         assert len(result.get_intensity_array()) == 2
#         assert result.get_intensity_error() is None

#     def test_cut_stage_process_immutability(self, sample_data, cut_stage):
#         """Test that CutStage doesn't modify the original sample."""
#         original_q = sample_data.get_q_values_array().copy()
#         original_i = sample_data.get_intensity_array().copy()
#         original_e = sample_data.get_intensity_error_array().copy()

#         result = cut_stage.process(sample_data)

#         # Original sample should be unchanged
#         np.testing.assert_array_equal(
#             sample_data.get_q_values_array(), original_q
#         )
#         np.testing.assert_array_equal(
#             sample_data.get_intensity_array(), original_i
#         )
#         np.testing.assert_array_equal(
#             sample_data.get_intensity_error_array(), original_e
#         )

#         # Result should be different (cut)
#         assert len(result.get_q_values_array()) < len(original_q)

#     def test_cut_stage_process_metadata_access(self, sample_data, cut_stage):
#         """Test that CutStage accesses metadata correctly."""
#         # Mock the metadata.get method
#         with patch.object(cut_stage.metadata, "get") as mock_get:
#             mock_get.return_value = 3  # Return cut_point = 3

#             result = cut_stage.process(sample_data)

#             assert isinstance(result, SAXSSample)
#             # Should have called metadata.get for cut_point
#             mock_get.assert_called_once_with("cut_point")
#             assert len(result.get_q_values_array()) == 3

#     def test_cut_stage_process_edge_cases(self, sample_data):
#         """Test CutStage with edge cases."""
#         # Test with cut_point = 1
#         stage1 = CutStage(cut_point=1)
#         result1 = stage1.process(sample_data)
#         assert len(result1.get_q_values_array()) == 1
#         assert (
#             result1.get_q_values_array()[0]
#             == sample_data.get_q_values_array()[0]
#         )

#         # Test with cut_point equal to data length
#         stage_full = CutStage(cut_point=len(sample_data.get_q_values_array()))
#         result_full = stage_full.process(sample_data)
#         assert len(result_full.get_q_values_array()) == len(
#             sample_data.get_q_values_array()
#         )
#         np.testing.assert_array_equal(
#             result_full.get_q_values_array(), sample_data.get_q_values_array()
#         )

#     def test_cut_stage_process_with_empty_data(self):
#         """Test CutStage with empty sample data."""
#         sample = SAXSSample(
#             q_values=QValues(np.array([])), intensity=Intensity(np.array([]))
#         )

#         stage = CutStage(cut_point=5)
#         result = stage.process(sample)

#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 0
#         assert len(result.get_intensity_array()) == 0

#     def test_cut_stage_process_consistency(self, sample_data):
#         """Test that CutStage produces consistent results."""
#         stage = CutStage(cut_point=3)

#         result1 = stage.process(sample_data)
#         result2 = stage.process(sample_data)

#         # Should produce identical results
#         np.testing.assert_array_equal(
#             result1.get_q_values_array(), result2.get_q_values_array()
#         )
#         np.testing.assert_array_equal(
#             result1.get_intensity_array(), result2.get_intensity_array()
#         )
#         np.testing.assert_array_equal(
#             result1.get_intensity_error_array(),
#             result2.get_intensity_error_array(),
#         )

#     def test_cut_stage_process_different_data_types(self):
#         """Test CutStage with different data types."""
#         # Test with float32 data
#         q_values = np.array([0.1, 0.2, 0.3], dtype=np.float32)
#         intensity = np.array([10.0, 8.0, 6.0], dtype=np.float32)

#         sample = SAXSSample(
#             q_values=QValues(q_values), intensity=Intensity(intensity)
#         )

#         stage = CutStage(cut_point=2)
#         result = stage.process(sample)

#         assert isinstance(result, SAXSSample)
#         assert len(result.get_q_values_array()) == 2
#         assert result.get_q_values_array().dtype == np.float32

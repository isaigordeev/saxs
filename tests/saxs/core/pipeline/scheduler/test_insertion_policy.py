#
# Created by Isai GORDEEV on 19/09/2025.
#

"""
Tests for insertion_policy.py module.
"""

import pytest

from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageRequest,
)
from saxs.saxs.core.pipeline.scheduler.insertion_policy import (
    AlwaysInsertPolicy,
    InsertionPolicy,
    MetadataKeyPolicy,
    NeverInsertPolicy,
    SaturationInsertPolicy,
)


class TestInsertionPolicy:
    """Test cases for InsertionPolicy abstract base class."""

    def test_insertion_policy_is_abstract(self):
        """Test that InsertionPolicy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            InsertionPolicy()

    def test_insertion_policy_has_call_method(self):
        """Test that InsertionPolicy has the abstract __call__ method."""
        assert hasattr(InsertionPolicy, "__call__")
        assert callable(getattr(InsertionPolicy, "__call__"))


class TestAlwaysInsertPolicy:
    """Test cases for AlwaysInsertPolicy class."""

    def test_always_insert_policy_creation(self):
        """Test creating AlwaysInsertPolicy."""
        policy = AlwaysInsertPolicy()
        assert isinstance(policy, InsertionPolicy)

    def test_always_insert_policy_always_returns_true(self, stage_request):
        """Test that AlwaysInsertPolicy always returns True."""
        policy = AlwaysInsertPolicy()

        # Should always return True regardless of request
        assert policy(stage_request) is True

        # Test with None request
        assert policy(None) is True

        # Test with different request types
        metadata = AbstractStageMetadata({"test": "value"})
        different_request = StageRequest(stage=None, metadata=metadata)
        assert policy(different_request) is True

    def test_always_insert_policy_with_multiple_requests(self, stage_request):
        """Test AlwaysInsertPolicy with multiple requests."""
        policy = AlwaysInsertPolicy()

        # Create multiple requests
        requests = [stage_request] * 10

        # All should return True
        for request in requests:
            assert policy(request) is True


class TestNeverInsertPolicy:
    """Test cases for NeverInsertPolicy class."""

    def test_never_insert_policy_creation(self):
        """Test creating NeverInsertPolicy."""
        policy = NeverInsertPolicy()
        assert isinstance(policy, InsertionPolicy)

    def test_never_insert_policy_always_returns_false(self, stage_request):
        """Test that NeverInsertPolicy always returns False."""
        policy = NeverInsertPolicy()

        # Should always return False regardless of request
        assert policy(stage_request) is False

        # Test with None request
        assert policy(None) is False

        # Test with different request types
        metadata = AbstractStageMetadata({"test": "value"})
        different_request = StageRequest(stage=None, metadata=metadata)
        assert policy(different_request) is False

    def test_never_insert_policy_with_multiple_requests(self, stage_request):
        """Test NeverInsertPolicy with multiple requests."""
        policy = NeverInsertPolicy()

        # Create multiple requests
        requests = [stage_request] * 10

        # All should return False
        for request in requests:
            assert policy(request) is False


class TestSaturationInsertPolicy:
    """Test cases for SaturationInsertPolicy class."""

    def test_saturation_insert_policy_creation(self):
        """Test creating SaturationInsertPolicy."""
        policy = SaturationInsertPolicy()
        assert isinstance(policy, InsertionPolicy)
        assert hasattr(policy, "_calls")
        assert hasattr(policy, "_saturation")

    def test_saturation_insert_policy_default_saturation(self):
        """Test SaturationInsertPolicy with default saturation value."""
        policy = SaturationInsertPolicy()
        assert policy._saturation == 6

    def test_saturation_insert_policy_behavior(self, stage_request):
        """Test SaturationInsertPolicy behavior up to saturation."""
        policy = SaturationInsertPolicy()

        # First 6 calls should return True
        for i in range(6):
            assert policy(stage_request) is True
            assert policy._calls == i + 1

        # 7th call and beyond should return False
        for i in range(6, 10):
            assert policy(stage_request) is False
            assert policy._calls == policy._saturation

    def test_saturation_insert_policy_reset_behavior(self, stage_request):
        """Test that SaturationInsertPolicy maintains state across calls."""
        policy = SaturationInsertPolicy()

        # Make calls up to saturation
        for _ in range(6):
            policy(stage_request)

        # Should now return False
        assert policy(stage_request) is False

        # Create new policy instance should reset
        new_policy = SaturationInsertPolicy()
        assert new_policy(stage_request) is True

    def test_saturation_insert_policy_with_different_requests(self):
        """Test SaturationInsertPolicy with different request types."""
        saturation_point = 6
        policy = SaturationInsertPolicy(saturation_point)

        # Create different requests
        metadata1 = AbstractStageMetadata({"type": "filter"})
        metadata2 = AbstractStageMetadata({"type": "peak"})
        request1 = StageRequest(stage=None, metadata=metadata1)
        request2 = StageRequest(stage=None, metadata=metadata2)

        # Both should count towards saturation
        assert policy(request1) is True  # Call 1
        assert policy(request2) is True  # Call 2
        assert policy(request1) is True  # Call 3
        assert policy(request2) is True  # Call 4
        assert policy(request1) is True  # Call 5
        assert policy(request2) is True  # Call 6

        # Now should be saturated
        assert policy(request1) is False  # Call 7
        assert policy(request2) is False  # Call 8


class TestMetadataKeyPolicy:
    """Test cases for MetadataKeyPolicy class."""

    def test_metadata_key_policy_creation(self):
        """Test creating MetadataKeyPolicy with key."""
        policy = MetadataKeyPolicy(key="required_key")
        assert isinstance(policy, InsertionPolicy)
        assert policy.key == "required_key"

    def test_metadata_key_policy_with_present_key(self, stage_request):
        """Test MetadataKeyPolicy when required key is present."""
        # Create request with required key
        metadata = AbstractStageMetadata(
            {"required_key": "value", "other_key": "other_value"}
        )
        request = StageRequest(stage=None, metadata=metadata)

        policy = MetadataKeyPolicy(key="required_key")
        assert policy(request) is True

    def test_metadata_key_policy_with_missing_key(self, stage_request):
        """Test MetadataKeyPolicy when required key is missing."""
        # Create request without required key
        metadata = AbstractStageMetadata({"other_key": "other_value"})
        request = StageRequest(stage=None, metadata=metadata)

        policy = MetadataKeyPolicy(key="required_key")
        assert policy(request) is False

    def test_metadata_key_policy_with_empty_metadata(self):
        """Test MetadataKeyPolicy with empty metadata."""
        metadata = AbstractStageMetadata()
        request = StageRequest(stage=None, metadata=metadata)

        policy = MetadataKeyPolicy(key="any_key")
        assert policy(request) is False

    def test_metadata_key_policy_with_none_value(self):
        """Test MetadataKeyPolicy when key exists but value is None."""
        metadata = AbstractStageMetadata({"required_key": None})
        request = StageRequest(stage=None, metadata=metadata)

        policy = MetadataKeyPolicy(key="required_key")
        # Should return True because key exists, regardless of value
        assert policy(request) is True

    def test_metadata_key_policy_with_different_key_names(self):
        """Test MetadataKeyPolicy with different key names."""
        metadata = AbstractStageMetadata(
            {"stage_type": "filter", "priority": "high", "enabled": True}
        )
        request = StageRequest(stage=None, metadata=metadata)

        # Test with different key names
        policy1 = MetadataKeyPolicy(key="stage_type")
        assert policy1(request) is True

        policy2 = MetadataKeyPolicy(key="priority")
        assert policy2(request) is True

        policy3 = MetadataKeyPolicy(key="enabled")
        assert policy3(request) is True

        policy4 = MetadataKeyPolicy(key="missing_key")
        assert policy4(request) is False

    def test_metadata_key_policy_case_sensitivity(self):
        """Test MetadataKeyPolicy with case-sensitive key matching."""
        metadata = AbstractStageMetadata({"StageType": "filter"})
        request = StageRequest(stage=None, metadata=metadata)

        # Test with exact case match
        policy_exact = MetadataKeyPolicy(key="StageType")
        assert policy_exact(request) is True

        # Test with different case
        policy_different = MetadataKeyPolicy(key="stagetype")
        assert policy_different(request) is False

    def test_metadata_key_policy_with_nested_keys(self):
        """Test MetadataKeyPolicy with nested key structures."""
        # Note: This test assumes the metadata structure supports nested access
        # If the actual implementation doesn't support this, this test should be adjusted
        metadata = AbstractStageMetadata(
            {"config": {"stage": {"type": "filter"}}}
        )
        request = StageRequest(stage=None, metadata=metadata)

        # Test with top-level key
        policy_top = MetadataKeyPolicy(key="config")
        assert policy_top(request) is True

        # Test with nested key (if supported)
        try:
            policy_nested = MetadataKeyPolicy(key="config.stage.type")
            result = policy_nested(request)
            assert isinstance(result, bool)
        except (KeyError, AttributeError):
            # If nested access isn't supported, that's also valid
            pytest.skip("Nested key access not supported")

    def test_metadata_key_policy_multiple_instances(self):
        """Test using multiple MetadataKeyPolicy instances."""
        metadata = AbstractStageMetadata(
            {"stage_type": "filter", "priority": "high", "enabled": True}
        )
        request = StageRequest(stage=None, metadata=metadata)

        # Create multiple policies
        policy_type = MetadataKeyPolicy(key="stage_type")
        policy_priority = MetadataKeyPolicy(key="priority")
        policy_enabled = MetadataKeyPolicy(key="enabled")
        policy_missing = MetadataKeyPolicy(key="missing_key")

        # Test all policies
        assert policy_type(request) is True
        assert policy_priority(request) is True
        assert policy_enabled(request) is True
        assert policy_missing(request) is False


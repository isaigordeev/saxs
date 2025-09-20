#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for abstract_data.py module.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pytest

from saxs.saxs.core.data.abstract_data import AData


class TestAData:
    """Test cases for AData abstract base class."""

    def test_adata_is_abstract(self):
        """Test that AData cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AData()

    def test_adata_has_describe_method(self):
        """Test that AData has the abstract describe method."""
        assert hasattr(AData, "describe")
        assert callable(getattr(AData, "describe"))

    def test_concrete_implementation_works(self):
        """Test that a concrete implementation of AData works correctly."""

        @dataclass
        class ConcreteData(AData):
            value: int = 42

            def describe(self) -> str:
                return f"ConcreteData with value: {self.value}"

        data = ConcreteData()
        assert data.describe() == "ConcreteData with value: 42"
        assert data.value == 42

    def test_concrete_implementation_without_describe_fails(self):
        """Test that a concrete implementation without describe method fails."""

        @dataclass
        class IncompleteData(AData):
            value: int = 42
            # Missing describe method

        with pytest.raises(TypeError):
            IncompleteData()

    def test_multiple_inheritance_with_adata(self):
        """Test that AData works with multiple inheritance."""

        class BaseClass:
            def __init__(self, name: str):
                self.name = name

        @dataclass
        class MultiInheritData(BaseClass, AData):
            value: int = 0

            def describe(self) -> str:
                return f"MultiInheritData: {self.name} with value {self.value}"

        data = MultiInheritData("test")
        assert data.name == "test"
        assert data.value == 0
        assert data.describe() == "MultiInheritData: test with value 0"

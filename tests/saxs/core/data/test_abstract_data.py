#
# Created by Isai GORDEEV on 20/09/2025.
#

"""Tests for abstract_data.py module."""

from dataclasses import dataclass

import pytest
from saxs.saxs.core.types.abstract_data import AData


class TestAData:
    """Test cases for AData abstract base class."""

    def test_adata_is_abstract(self) -> None:
        """Test that AData cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AData()

    def test_adata_has_describe_method(self) -> None:
        """Test that AData has the abstract describe method."""
        assert hasattr(AData, "describe")
        assert callable(AData.describe)

    def test_concrete_implementation_works(self) -> None:
        """Test that a concrete implementation of AData works correctly."""

        @dataclass(frozen=True)
        class ConcreteData(AData):
            value: int = 42

            def describe(self) -> str:
                return f"ConcreteData with value: {self.value}"

        data = ConcreteData()
        assert data.describe() == "ConcreteData with value: 42"
        assert data.value == 42

    def test_concrete_implementation_without_describe_fails(self) -> None:
        """Test that a concrete implementation without describe method fails."""

        @dataclass(frozen=True)
        class IncompleteData(AData):
            value: int = 42
            # Missing describe method

        with pytest.raises(TypeError):
            IncompleteData()

    def test_multiple_inheritance_with_adata(self) -> None:
        """Test that AData works with multiple inheritance."""

        class BaseClass:
            name = "test"

        @dataclass(frozen=True)
        class MultiInheritData(BaseClass, AData):
            value: int = 0

            def describe(self) -> str:
                return f"MultiInheritData: {self.name} with value {self.value}"

        data = MultiInheritData()
        assert data.name == "test"
        assert data.value == 0
        assert data.describe() == "MultiInheritData: test with value 0"

"""
Module: base_data_type.

This module defines the `BaseDataType` generic class — a
foundational data container used across the SAXS  processing
pipeline.

`BaseDataType` provides a minimal, immutable wrapper for any
 underlying data structure (e.g., NumPy arrays, dictionaries). It
 serves as a uniform interface for accessing and handling diverse
 types of scientific data through the `.unwrap()` method, promoting
 consistent API behavior across all derived types.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class BaseDataType(Generic[T]):
    """
    Generic, immutable data wrapper for scientific data objects.

    This class provides a lightweight abstraction layer over raw
    data containers such as NumPy arrays, dictionaries, or other
    structured data objects. Subclasses typically specify a concrete
    type parameter `T` to enforce type safety for the wrapped value.

    Attributes
    ----------
        values (T | None): The underlying data structure. May be
        None if the data object is uninitialized.
    """

    values: T | None = None

    def unwrap(self) -> T | None:
        """
        Return the underlying data object.

        Returns
        -------
            T | None: The wrapped data (e.g., NumPy array, dict) or
            None if no data is present.
        """
        return self.values

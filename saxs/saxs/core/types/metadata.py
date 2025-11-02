"""
Module: flow_metadata.

This module defines the data structures used to store metadata for
flow experiments. It includes a TypedDict for type-safe metadata
keys and a frozen dataclass to wrap the metadata in an immutable
container.
"""

from enum import Enum
from typing import Any, TypedDict, TypeVar

from saxs.saxs.core.types.abstract_data import TBaseDataType


class EMetadataSchemaKeys(Enum):
    """Abstract metadata Schema."""


class MetadataSchemaDict(TypedDict, total=False):
    """Abstract dictionary schema."""


MetadataValueType = Any

TMetadataSchemaDict = TypeVar("TMetadataSchemaDict", bound=MetadataSchemaDict)


class AbstractMetadata(TBaseDataType[TMetadataSchemaDict]):
    """Set a value for a specific metadata key.

    This allows dict-like assignment on the sample:

    ```python
    sample['q_values'] = QValues(...)
    ```

    The underlying data is updated immutably, returning a new
    SAXSSample if necessary, though this method does not modify
    the current instance in-place.

    Parameters
    ----------
    key : TMetadataSchemaKeys
        The key identifying the metadata array to update.
    value : MetadataValueType
        The new value to assign to the metadata key.

    Raises
    ------
    KeyError
        If the provided key is not a valid array-like metadata key.
    TypeError
        If the value type is incompatible with the expected
        metadata value type.
    """

    def __getitem__(self, key: EMetadataSchemaKeys) -> MetadataValueType:
        """Get a metadata value by key."""
        _value = self.unwrap()  # may raise AttributeError
        try:
            return _value[key.value]
        except KeyError:
            valid_keys = [k.value for k in EMetadataSchemaKeys]
            msg = f"Invalid metadata key: {key}. Supported keys: {valid_keys}."
            raise KeyError(msg) from None

    def __setitem__(self, key: EMetadataSchemaKeys, value: MetadataValueType):
        """Setter dict for array like data in the sample.

        Allow dict-like mutation: sample['q_values'] = QValues(...)
        This returns a new immutable SAXSSample
        (does modify in-place).
        """
        try:
            _value = self.unwrap()
        except AttributeError as e:
            msg = (
                "Failed to unwrap AbstractMetadata instance. "
                "Ensure the object is properly initialized."
            )
            raise RuntimeError(msg) from e

        # Attempt to set the value
        try:
            _value[key.value] = value
        except KeyError:
            valid_keys = [k.value for k in EMetadataSchemaKeys]
            msg = (
                f"Invalid metadata key: {key}. "
                f"Supported keys are: {valid_keys}."
            )
            raise KeyError(msg) from None
        except TypeError as e:
            msg = (
                f"Invalid type for value assigned to key {key}. "
                f"Expected MetadataValueType, got {type(value).__name__}."
            )
            raise TypeError(msg) from e

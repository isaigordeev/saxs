"""
Module: metadata.

This module defines the data structures used to store metadata. It
includes a TypedDict for type-safe metadata keys and a frozen
dataclass to wrap the metadata in an immutable
container.
"""

from enum import Enum
from typing import Any, Generic, TypedDict, TypeVar

from saxs.saxs.core.types.abstract_data import TBaseDataType


class EMetadataSchemaKeys(Enum):
    """Abstract metadata Schema."""


class MetadataSchemaDict(TypedDict, total=False):
    """Abstract dictionary schema."""


MetadataValueType = Any

TMetadataSchemaDict = TypeVar("TMetadataSchemaDict", bound=MetadataSchemaDict)
TMetadataKeys = TypeVar("TMetadataKeys", bound=EMetadataSchemaKeys)


class Metadata(type):
    """Define metadata metaclass."""

    def __new__(
        mcls: type["Metadata"],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ):
        """
        Create a new class with metadata schema enforcement.

        Parameters
        ----------
        mcls : Type[MetadataMeta]
            The metaclass itself — typically not used directly, but
            needed for calling `super().__new__`.

        name : str
            The name of the class being defined. For example:
            - "AbstractMetadata"
            - "SampleMetadata"

        bases : tuple[type, ...]
            The base classes that the new class inherits from.
            Used to check inheritance hierarchies or propagate
            behavior.

        namespace : Dict[str, Any]
            A mapping of all class-level definitions (methods,
            nested classes, attributes) that appear in the class
            body before the class object
            is actually created. For example:
            ```python
            {
                '__module__': 'flow_metadata',
                '__doc__': '...',
                'Keys': <enum 'Keys'>,
                'Schema': <class 'Schema'>,
                '__getitem__': <function ...>,
                ...
            }
            ```

        Returns
        -------
        MetadataMeta
            The newly created class object (not an instance — but
            the class itself).
        """
        cls = super().__new__(mcls, name, bases, namespace)

        if name not in {
            "AbstractMetadata",
            "TAbstractMetadata",
            "TAbstractStageMetadata",
        }:
            keys_cls = namespace.get("Keys")
            schema_cls = namespace.get("Dict")

            if keys_cls is None or not issubclass(
                keys_cls,
                EMetadataSchemaKeys,
            ):
                msg = f"{name} must define nested Enum class 'Keys'."
                raise TypeError(msg)

            if schema_cls is None or not issubclass(schema_cls, dict):
                msg = f"{name} must define nested TypedDict class 'Schema'."
                raise TypeError(msg)
        return cls


class TAbstractMetadata(
    TBaseDataType[TMetadataSchemaDict],
    Generic[TMetadataSchemaDict, TMetadataKeys],
    metaclass=Metadata,
):
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

    Keys: type[TMetadataKeys]
    Dict: type[TMetadataSchemaDict]

    def __contains__(self, key: TMetadataKeys):
        """Contains method."""
        return key.value in self.unwrap()

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

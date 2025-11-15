"""
Module: saxs_sample_typed.

Defines SAXS sample objects using TypedDict with builder-style
setters.

This module provides a TypedDict-based version of SAXSSample,
representing a small-angle X-ray scattering (SAXS) sample with
q-values, intensity, optional intensity error, and associated
metadata. The builder-style methods allow creating modified copies
of the sample while keeping the original data intact.
"""

from collections.abc import ItemsView, KeysView, ValuesView
from enum import Enum
from typing import Any, TypedDict, Union, get_type_hints

import numpy as np
from numpy.typing import NDArray

from saxs.saxs.core.types.abstract_data import TBaseDataType
from saxs.saxs.core.types.sample_objects import (
    ESampleMetadataKeys,
    Intensity,
    IntensityError,
    QValues,
    SampleMetadata,
)


class ESAXSSampleKeys(Enum):
    """SAXS Samle enum.

    Enumeration of keys used to represent data fields in a
    Small Angle X-ray Scattering (SAXS) sample.

    Attributes
    ----------
        Q_VALUES: Key for the scattering vector (q) values array.
        INTENSITY: Key for the array of intensity values
        corresponding to each q value.
        INTENSITY_ERROR: Key for the array of uncertainties or
        errors in the intensity measurements.
        METADATA: Key for any additional sample-related metadata.
    """

    Q_VALUES = "q_values"
    INTENSITY = "intensity"
    INTENSITY_ERROR = "intensity_err"
    METADATA = "metadata"
    CURRENT = "current_peak"


class SAXSSampleDict(TypedDict):
    """
    TypedDict representing a SAXS sample.

    Attributes
    ----------
        q_values (QValues): The q-values of the sample.
        intensity (Intensity): The measured intensities.
        intensity_error (Optional[IntensityError]): Optional
        measurement errors.
        metadata (AbstractSampleMetadata): Metadata associated with
        the sample.
    """

    q_values: QValues
    intensity: Intensity
    intensity_err: IntensityError
    metadata: SampleMetadata


SAXSSampleArrayValue = Union[
    QValues,
    Intensity,
    IntensityError,
]

SAXSSampleValue = Union[SampleMetadata, SAXSSampleArrayValue]


class SAXSSample(TBaseDataType[SAXSSampleDict]):
    """
    Represents a Small-Angle X-ray Scattering (SAXS) sample.

    This class provides a typed, dict-like interface to access and
    manipulate SAXS sample data, including q-values, intensity,
    optional intensity errors, and metadata. It is built on top
    of `TBaseDataType` and `TypedDict` for type safety.

    Features
    --------
    - Dict-like access for array-like data using `__getitem__`
      and `__setitem__`.
    - Supports builder-style mutation: updates return new instances
      or wrapped array types (QValues, Intensity, IntensityError).
    - Provides convenience methods for iteration, containment
      checks, and accessing keys, values, and items.

    Examples
    --------
    >>> sample = SAXSSample({
    ...     "q_values": QValues(np.array([0.1, 0.2])),
    ...     "intensity": Intensity(np.array([100.0, 150.0])),
    ...     "intensity_err": IntensityError(np.array([5.0, 7.0])),
    ...     "metadata": AbstractSampleMetadata()
    ... })
    >>> sample[ESAXSSampleKeys.Q_VALUES]
    QValues(array([0.1, 0.2]))
    >>> sample[ESAXSSampleKeys.INTENSITY] = np.array([110.0, 160.0])

    Notes
    -----
    - Only array-like keys (q_values, intensity, intensity_err) are
      directly gettable and settable using the dict-like interface.
    - Metadata must be accessed via the 'metadata' key.
    """

    Keys: type[ESAXSSampleKeys] = ESAXSSampleKeys

    def __getitem__(
        self,
        key: ESAXSSampleKeys,
    ) -> NDArray[np.float64]:
        """Allow dict-like access: sample['q_values']."""
        _sample: SAXSSampleDict = self.unwrap()
        if (
            key is ESAXSSampleKeys.Q_VALUES
            or key is ESAXSSampleKeys.INTENSITY
            or key is ESAXSSampleKeys.INTENSITY_ERROR
            # or key is ESAXSSampleKeys.METADATA
        ):
            return _sample[key.value].unwrap()

        msg = f"Invalid SAXSSample key: {key}. Only array like keys \
                    supported"
        raise KeyError(msg)

    def __setitem__(self, key: ESAXSSampleKeys, _value: NDArray[np.float64]):
        """Setter dict for array like data in the sample.

        Allow dict-like mutation: sample['q_values'] = QValues(...)
        This returns a new immutable SAXSSample
        (does modify in-place).
        """
        _sample: SAXSSampleDict = self.unwrap()
        if key is ESAXSSampleKeys.Q_VALUES:
            _sample[key.value] = QValues(_value)
        elif key is ESAXSSampleKeys.INTENSITY:
            _sample[key.value] = Intensity(_value)
        elif key is ESAXSSampleKeys.INTENSITY_ERROR:
            _sample[key.value] = IntensityError(_value)
        else:
            msg = f"Invalid SAXSSample key: {key}. Only array like keys \
                    supported"
            raise KeyError(msg)

    def get_metadata(self) -> SampleMetadata:
        """Getter for metadata."""
        _sample: SAXSSampleDict = self.unwrap()

        return _sample[ESAXSSampleKeys.METADATA.value]

    def set_metadata(self, key: ESampleMetadataKeys, _value: Any) -> None:  # noqa: ANN401
        """Setter for metadata."""
        _sample_metadata: SampleMetadata = self.get_metadata()

        hints = get_type_hints(SAXSSampleDict)

        # --- Runtime type safety ---
        expected_type = hints.get(key.value)

        if expected_type is not None and not isinstance(
            _value,
            expected_type.__origin__
            if hasattr(expected_type, "__origin__")
            else expected_type,
        ):
            msg = f"Invalid type for '{key}': expected {expected_type}, got {type(_value)}"
            raise TypeError(msg)

        _sample_metadata[key] = _value

    def __contains__(self, key: str) -> bool:
        """Support `'key' in sample` syntax."""
        return key in self.unwrap()

    def __iter__(self):
        """Iterate over keys."""
        return iter(self.unwrap())

    def keys(self) -> KeysView[str]:
        """Expose dict keys."""
        return self.unwrap().keys()

    def values(self) -> ValuesView[object]:
        """Expose dict values."""
        return self.unwrap().values()

    def items(self) -> ItemsView[str, object]:
        """Expose dict items."""
        return self.unwrap().items()

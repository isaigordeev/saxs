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

from enum import Enum
from typing import Any, TypedDict, Union

import numpy as np
from numpy.typing import NDArray

from saxs.saxs.core.types.abstract_data import BaseDataType
from saxs.saxs.core.types.sample_objects import (
    AbstractSampleMetadata,
    Intensity,
    IntensityError,
    QValues,
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
    metadata: AbstractSampleMetadata


SAXSSampleArrayValue = Union[
    QValues,
    Intensity,
    IntensityError,
]

SAXSSampleValue = Union[AbstractSampleMetadata, SAXSSampleArrayValue]


class SAXSSample(BaseDataType[SAXSSampleDict]):
    # --- Getters ---
    def get_q_values(self) -> NDArray[np.float64]:
        """Return the raw q-values array from the sample."""
        _sample: SAXSSampleDict = self.unwrap()
        _q_values: QValues = _sample.get(ESAXSSampleKeys.Q_VALUES.value)
        return _q_values.unwrap()

    def get_intensity(self) -> NDArray[np.float64]:
        """Return the raw intensity array from the sample."""
        _sample: SAXSSampleDict = self.unwrap()
        _intensity: Intensity = _sample.get(ESAXSSampleKeys.INTENSITY.value)
        return _intensity.unwrap()

    def get_intensity_error(self) -> NDArray[np.float64] | None:
        """Return the raw intensity error array, or None if missing."""  # noqa: W505
        _sample: SAXSSampleDict = self.unwrap()
        _error: IntensityError | None = _sample.get(
            ESAXSSampleKeys.INTENSITY_ERROR.value,
        )
        return _error.unwrap() if _error else None

    def get_metadata(self) -> AbstractSampleMetadata:
        """Return the metadata dict."""
        _sample: SAXSSampleDict = self.unwrap()
        return _sample.get(ESAXSSampleKeys.METADATA.value)

    # --- Immutable Setters ---

    def set_q_values(self, q_array: NDArray[np.float64]) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                ESAXSSampleKeys.Q_VALUES.value: QValues(q_array),
            },
        )

    def set_intensity(
        self,
        intensity_array: NDArray[np.float64],
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                ESAXSSampleKeys.INTENSITY.value: Intensity(intensity_array),
            },
        )

    def set_intensity_error(
        self,
        error_array: NDArray[np.float64] | None,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                ESAXSSampleKeys.INTENSITY_ERROR.value: IntensityError(
                    error_array,
                ),
            },
        )

    def set_metadata_dict(
        self,
        metadata_dict: AbstractSampleMetadata,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                ESAXSSampleKeys.METADATA.value: metadata_dict,
            },
        )

    def set_new_sample(
        self,
        _new_sample_dict: SAXSSampleDict,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **_new_sample_dict,
            },
        )

    def update_new_sample(
        self,
        _sample_dict_to_append: SAXSSampleDict,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                **_sample_dict_to_append,
            },
        )

    # --- Dict-style Access ---

    def __getitem__(
        self,
        key: ESAXSSampleKeys,
    ) -> dict[str, Any] | NDArray[np.float64] | None:
        """Allow dict-like access: sample['q_values']."""
        _sample: SAXSSampleDict = self.unwrap()
        _value: SAXSSampleValue = _sample[key.value]
        return _value.unwrap()

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

    def __contains__(self, key: str) -> bool:
        """Support `'key' in sample` syntax."""
        return key in self.unwrap()

    def __iter__(self):
        """Iterate over keys."""
        return iter(self.unwrap())

    def keys(self):
        return self.unwrap().keys()

    def values(self):
        return self.unwrap().values()

    def items(self):
        return self.unwrap().items()

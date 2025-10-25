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


class SAXSSampleKeys(Enum):
    Q_VALUES = "q_values"
    INTENSITY = "intensity"
    INTENSITY_ERROR = "intensity_error"
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
    intensity_error: IntensityError
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
        _q_values: QValues = _sample.get("q_values")
        return _q_values.unwrap()

    def get_intensity(self) -> NDArray[np.float64]:
        """Return the raw intensity array from the sample."""
        _sample: SAXSSampleDict = self.unwrap()
        _intensity: Intensity = _sample.get("intensity")
        return _intensity.unwrap()

    def get_intensity_error(self) -> NDArray[np.float64] | None:
        """Return the raw intensity error array, or None if missing."""  # noqa: W505
        _sample: SAXSSampleDict = self.unwrap()
        _error: IntensityError | None = _sample.get("intensity_error")
        return _error.unwrap() if _error else None

    def get_metadata(self) -> AbstractSampleMetadata:
        """Return the metadata dict."""
        _sample: SAXSSampleDict = self.unwrap()
        return _sample.get("metadata")

    # --- Immutable Setters ---

    def set_q_values(self, q_array: NDArray[np.float64]) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                "q_values": QValues(q_array),
            },
        )

    def set_intensity(
        self,
        intensity_array: NDArray[np.float64],
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                "intensity": Intensity(intensity_array),
            },
        )

    def set_intensity_error(
        self,
        error_array: NDArray[np.float64] | None,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                "intensity_error": IntensityError(error_array)
                if error_array is not None
                else None,
            },
        )

    def set_metadata_dict(
        self,
        metadata_dict: AbstractSampleMetadata,
    ) -> "SAXSSample":
        return SAXSSample(
            {
                **self.unwrap(),
                "metadata": metadata_dict,
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
        key: SAXSSampleKeys,
    ) -> dict[str, Any] | NDArray[np.float64] | None:
        """Allow dict-like access: sample['q_values']."""
        _sample: SAXSSampleDict = self.unwrap()
        _value: SAXSSampleValue = _sample[key.value]
        return _value.unwrap()

    def __setitem__(self, key: SAXSSampleKeys, value: NDArray[np.float64]):
        """Setter dict.

        Allow dict-like mutation: sample['q_values'] = QValues(...)
        This returns a new immutable SAXSSample
        (does modify in-place).
        """
        _sample: SAXSSampleDict = self.unwrap()
        if key is SAXSSampleKeys.Q_VALUES:
            _sample[key.value] = QValues(value)
        elif key is SAXSSampleKeys.INTENSITY:
            _sample[key.value] = Intensity(value)
        elif key is SAXSSampleKeys.INTENSITY_ERROR:
            _sample[key.value] = IntensityError(value)
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

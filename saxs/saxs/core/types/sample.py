#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

import numpy as np

from saxs.saxs.core.types.abstract_data import AData
from saxs.saxs.core.types.sample_objects import (
    AbstractSampleMetadata,
    Intensity,
    IntensityError,
    QValues,
)


@dataclass(frozen=True)
class SAXSSample(AData):
    """Immutable SAXS sample with typed fields and builder-style setters."""

    q_values: QValues
    intensity: Intensity
    intensity_error: IntensityError = None
    metadata: AbstractSampleMetadata = field(
        default_factory=AbstractSampleMetadata
    )

    # --- Getters ---
    def get_q_values(self) -> "QValues":
        return self.q_values

    def get_intensity(self) -> "Intensity":
        return self.intensity

    def get_intensity_error(self) -> Optional["IntensityError"]:
        return self.intensity_error

    def get_metadata(self) -> "AbstractSampleMetadata":
        return self.metadata

    # --- Raw data getters (via unwrap) ---
    def get_q_values_array(self):
        return self.q_values.unwrap()

    def get_intensity_array(self):
        return self.intensity.unwrap()

    def get_intensity_error_array(self):
        return self.intensity_error.unwrap() if self.intensity_error else None

    def get_metadata_dict(self):
        return self.metadata.unwrap()

    # Setter-style methods
    # --- Raw data setters ---

    def set_q_values(self, q_array: np.ndarray) -> "SAXSSample":
        """Set q_values from raw ndarray."""
        return replace(self, q_values=QValues(q_array))

    def set_intensity(self, intensity_array: np.ndarray) -> "SAXSSample":
        """Set intensity from raw ndarray."""
        return replace(self, intensity=Intensity(intensity_array))

    def set_intensity_error(
        self, error_array: Optional[np.ndarray]
    ) -> "SAXSSample":
        """Set intensity_error from raw ndarray (or None)."""
        return replace(
            self,
            intensity_error=IntensityError(error_array)
            if error_array is not None
            else None,
        )

    def set_metadata_dict(self, metadata_dict: Dict[str, Any]) -> "SAXSSample":
        """Set metadata from raw dictionary."""
        return replace(
            self, metadata=AbstractSampleMetadata(values=metadata_dict)
        )

    def append_metadata_dict(
        self, new_metadata: Dict[str, Any]
    ) -> "SAXSSample":
        merged = AbstractSampleMetadata(
            {**self.get_metadata_dict(), **new_metadata}
        )
        return replace(self, metadata=merged)

    def set_metadata(
        self, new_metadata: AbstractSampleMetadata
    ) -> "SAXSSample":
        return replace(self, metadata=new_metadata)

    def describe(self) -> str:
        return "SAXS Sample"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SAXSSample):
            return False

        # Compare q_values
        if not np.array_equal(self.q_values.unwrap(), other.q_values.unwrap()):
            return False

        # Compare intensity
        if not np.array_equal(
            self.intensity.unwrap(), other.intensity.unwrap()
        ):
            return False

        # Compare intensity_error
        if self.intensity_error is None and other.intensity_error is not None:
            return False
        if self.intensity_error is not None and other.intensity_error is None:
            return False
        if (
            self.intensity_error is not None
            and other.intensity_error is not None
        ):
            if not np.array_equal(
                self.intensity_error.unwrap(), other.intensity_error.unwrap()
            ):
                return False

        # Compare metadata dictionaries
        if self.metadata.unwrap() != other.metadata.unwrap():
            return False

        return True

    def __str__(self) -> str:
        q_len = len(self.q_values.unwrap()) if self.q_values else 0
        i_len = len(self.intensity.unwrap()) if self.intensity else 0
        err_len = (
            len(self.intensity_error.unwrap()) if self.intensity_error else 0
        )
        meta_keys = (
            list(self.metadata.unwrap().keys()) if self.metadata else []
        )
        return (
            f"SAXSSample(q_values={q_len} points, "
            f"intensity={i_len} points, "
            f"intensity_error={err_len} points, "
            f"metadata_keys={meta_keys})"
        )

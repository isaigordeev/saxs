#
# Created by Isai GORDEEV on 19/09/2025.
#


from dataclasses import dataclass, field, replace

from saxs.saxs.data.abstract_data import AData
from saxs.saxs.data.sample_objects import (
    AbstractSampleMetadata,
    Intensity,
    IntensityError,
    QValues,
)


@dataclass(frozen=True)
class SAXSSample(AData):
    """
    Immutable SAXS sample with typed fields and builder-style setters.
    """

    q_values: QValues
    intensity: Intensity
    intensity_error: IntensityError = None
    metadata: AbstractSampleMetadata = field(default_factory=dict)

    # Setter-style methods
    def set_intensity(self, new_intensity: Intensity) -> "SAXSSample":
        return replace(self, intensity=new_intensity)

    def set_q_values(self, q_values: QValues) -> "SAXSSample":
        return replace(self, q_values=q_values)

    def append_metadata(
        self, new_metadata: AbstractSampleMetadata
    ) -> "SAXSSample":
        merged = {**self.metadata, **new_metadata}
        return replace(self, metadata=merged)

    def set_metadata(
        self, new_metadata: AbstractSampleMetadata
    ) -> "SAXSSample":
        return replace(self, metadata=new_metadata)

    def describe(self) -> str:
        return "SAXS Sample"

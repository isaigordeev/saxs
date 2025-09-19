#
# Created by Isai GORDEEV on 19/09/2025.
#


from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace

from saxs.algo.data.objects import Intensity, IntensityError, Metadata, QValues


@dataclass
class AData(ABC):
    id: int

    @abstractmethod
    def describe(self) -> str:
        pass


@dataclass(frozen=True)
class SAXSSample(AData):
    """
    Immutable SAXS sample with typed fields and builder-style setters.
    """

    q_values: QValues
    intensity: Intensity
    intensity_error: IntensityError = None
    metadata: Metadata = field(default_factory=dict)

    # Setter-style methods
    def set_intensity(self, new_intensity: Intensity) -> "SAXSSample":
        return replace(self, intensity=new_intensity)

    def set_q_values(self, q_values: QValues) -> "SAXSSample":
        return replace(self, q_values=q_values)

    def set_metadata(self, new_metadata: Metadata) -> "SAXSSample":
        merged = {**self.metadata, **new_metadata}
        return replace(self, metadata=merged)

    def describe(self) -> str:
        return "SAXS Sample"

#
# Created by Isai GORDEEV on 20/09/2025.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AData(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass

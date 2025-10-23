#
# Created by Isai GORDEEV on 20/09/2025.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AData(ABC):
    @abstractmethod
    def describe(self) -> str:
        pass


# --- Base wrapper for array-like data ---
@dataclass(frozen=True)
class BaseDataType:
    values: Any | None = None

    def unwrap(self) -> Any | None:
        """Return the underlying NumPy array (or None if missing)."""
        return self.values

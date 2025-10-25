#
# Created by Isai GORDEEV on 22/09/2025.
#


from dataclasses import dataclass, field
from typing import Any

from saxs.saxs.core.types.abstract_data import BaseDataType


@dataclass(frozen=True)
class AbstractSchedulerMetadata(BaseDataType[dict[str, Any]]):
    value: dict[str, Any] = field(default_factory=dict[str, Any])

    def describe(self) -> str:
        """Describe method."""
        return f"Stage scheduler metadata with keys: {list(self.value.keys())}"

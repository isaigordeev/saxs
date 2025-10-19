#
# Created by Isai GORDEEV on 22/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict

from saxs.saxs.core.types.abstract_data import BaseDataType


@dataclass(frozen=True)
class AbstractSchedulerMetadata(BaseDataType):
    values: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        return (
            f"Stage scheduler metadata with keys: {list(self.values.keys())}"
        )

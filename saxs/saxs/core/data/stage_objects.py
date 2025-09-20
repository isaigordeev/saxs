#
# Created by Isai GORDEEV on 20/09/2025.
#


from dataclasses import dataclass, field
from typing import Any, Dict

from saxs.saxs.core.data.abstract_data import BaseDataType


@dataclass(frozen=True)
class AbstractStageMetadata(BaseDataType):
    values: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        return f"Stage metadata with keys: {list(self.values.keys())}"

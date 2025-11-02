#
# Created by Isai GORDEEV on 22/09/2025.
#


from dataclasses import field
from enum import Enum
from typing import TypedDict

from saxs.saxs.core.types.abstract_data import BaseDataType


class ESchedulerMetadataDictKeys(Enum):
    PROCESSED = "processed"
    PEAKS = "peaks"


class SchedulerMetadataDict(TypedDict):
    processed: int


class AbstractSchedulerMetadata(BaseDataType[SchedulerMetadataDict]):
    value: SchedulerMetadataDict = field(
        default_factory=lambda: {
            ESchedulerMetadataDictKeys.PROCESSED.value: 0,
        },
    )

    def describe(self) -> str:
        """Describe method."""
        return f"Stage scheduler metadata with keys: {list(self.value.keys())}"

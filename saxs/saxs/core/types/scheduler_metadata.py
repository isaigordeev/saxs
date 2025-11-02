#
# Created by Isai GORDEEV on 22/09/2025.
#


from dataclasses import field

from saxs.saxs.core.types.metadata import (
    AbstractMetadata,
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)


class ESchedulerMetadataDictKeys(EMetadataSchemaKeys):
    PROCESSED = "processed"
    PEAKS = "peaks"


class SchedulerMetadataDict(MetadataSchemaDict):
    processed: int


class AbstractSchedulerMetadata(AbstractMetadata[SchedulerMetadataDict]):
    value: SchedulerMetadataDict = field(
        default_factory=lambda: {
            ESchedulerMetadataDictKeys.PROCESSED.value: 0,
        },
    )

    def describe(self) -> str:
        """Describe method."""
        return f"Stage scheduler metadata with keys: {list(self.value.keys())}"

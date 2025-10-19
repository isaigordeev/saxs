#
# Created by Isai GORDEEV on 22/09/2025.
#

from saxs.saxs.core.types.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)


class TrueCondition(StageCondition):
    def evaluate(self, metadata: AbstractSampleMetadata) -> bool:
        return True

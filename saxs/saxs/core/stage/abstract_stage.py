#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)


class AbstractStage(ABC):
    """Abstract base class for all processing stages."""

    metadata: AbstractStageMetadata

    def process(self, stage_data: SAXSSample) -> SAXSSample:
        """Process input data and return new SAXSSample."""
        return self._process(stage_data)

    @abstractmethod
    def _process(self, stage_data: SAXSSample) -> SAXSSample:
        """Process input data and return new SAXSSample."""
        pass

    def get_next_stage(self):
        return []

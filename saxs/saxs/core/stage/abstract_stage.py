#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    AbstractCondition,
)
from saxs.saxs.core.pipeline.scheduler.stage_request import StageRequest


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


class AbstractConditionalStage(AbstractStage):
    def __init__(
        self, stage_to_add: AbstractStage, condition: AbstractCondition
    ):
        self.stage_to_add = stage_to_add
        self.condition = condition

    def get_next_stage(self):
        if self.condition.evaluate(self.metadata):
            return [StageRequest(self.stage_to_add, self.metadata)]
        return []


class AbstractSelfRepeatingConditionalStage(AbstractStage):
    def __init__(self, condition: AbstractCondition):
        self.condition = condition

    def get_next_stage(self):
        # if condition is true, reinsert itself into the pipeline
        if self.condition.evaluate(self.metadata):
            return [StageRequest(self, self.metadata)]
        return []

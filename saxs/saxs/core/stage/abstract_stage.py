#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod

from saxs.saxs.data.sample_objects import AbstractSampleMetadata
from saxs.saxs.data.sample import SAXSSample
from saxs.saxs.data.stage_objects import AbstractStageMetadata
from saxs.saxs.pipeline.condition.abstract_condition import AbstractCondition
from saxs.saxs.pipeline.scheduler.stage_request import StageRequest


class AbstractStage(ABC):
    """Abstract base class for all processing stages."""

    metadata: AbstractStageMetadata

    @abstractmethod
    def process(self, data: SAXSSample) -> SAXSSample:
        """Process input data and return new SAXSSample."""
        pass

    @abstractmethod
    def _process(self, data: SAXSSample) -> SAXSSample:
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

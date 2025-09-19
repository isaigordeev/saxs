#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod

from saxs.algo.data.sample import SAXSSample
from saxs.algo.pipeline.condition.abstract_condition import AbstractCondition


class AbstractStage(ABC):
    """Abstract base class for all processing stages."""

    @abstractmethod
    def process(self, data: SAXSSample) -> SAXSSample:
        """Process input data and return new SAXSSample."""
        pass


class AbstractConditionalStage(AbstractStage):
    def __init__(
        self, stage_to_add: AbstractStage, condition: AbstractCondition
    ):
        self.stage_to_add = stage_to_add
        self.condition = condition

    def get_additional_stages(self, metadata):
        if self.condition.evaluate(metadata):
            return [self.stage_to_add]
        return []

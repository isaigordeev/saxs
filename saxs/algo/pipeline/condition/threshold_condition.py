#
# Created by Isai GORDEEV on 19/09/2025.
#

from saxs.algo.data.sample import SAXSSample
from saxs.algo.pipeline.condition.abstract_condition import AbstractCondition


class ThresholdCondition(AbstractCondition):
    def __init__(self, key: str, threshold: float):
        self.key = key
        self.threshold = threshold

    def evaluate(self, sample: "SAXSSample") -> bool:
        value = sample.metadata.get(self.key, 0)
        return value > self.threshold

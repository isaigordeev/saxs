from abc import ABC, abstractmethod

from saxs.algo.data.sample import SAXSSample


class AbstractCondition(ABC):
    @abstractmethod
    def evaluate(self, sample: "SAXSSample") -> bool:
        """Return True if the condition passes for the given sample."""
        pass

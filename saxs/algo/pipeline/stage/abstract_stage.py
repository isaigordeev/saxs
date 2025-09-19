#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod

from saxs.algo.data.stage import SAXSData


class Stage(ABC):
    """Abstract base class for all processing stages."""

    @abstractmethod
    def process(self, data: SAXSData) -> SAXSData:
        """Process input data and return new SAXSData."""
        pass

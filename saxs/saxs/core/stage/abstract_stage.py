#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)


class AbstractStage(ABC):
    metadata: "AbstractStageMetadata"

    def __init__(self, metadata: Optional[AbstractStageMetadata] = None):
        self.metadata = metadata if metadata else AbstractStageMetadata()

    def process(self, sample_data: SAXSSample):
        """
        Run the stage on stage_data.
        Handles metadata management via hooks.
        """
        result, metadata = self._process(sample_data)

        # Delegate metadata management to hook
        result = self.handle_metadata(result, metadata)

        return result

    @abstractmethod
    def _process(
        self, sample_data: SAXSSample
    ) -> Tuple["SAXSSample", Optional[Dict]]:
        """Override in subclass. Return (updated_sample,
        optional_metadata_dict)."""
        raise NotImplementedError

    def handle_metadata(
        self, sample: "SAXSSample", metadata: Optional[Dict]
    ) -> "SAXSSample":
        """
        Default metadata handler: updates both sample and stage metadata.
        Can be overridden in subclasses for custom behavior.
        """
        if metadata is None:
            return sample

        # Update sample metadata
        # updated_sample = sample.set_metadata_dict(
        #     {
        #         **sample.get_metadata_dict(),
        #         **metadata,
        #     }
        # )

        # Update stage metadata
        self.metadata = AbstractStageMetadata(values=metadata)

        return sample

    def request_stage(self):
        return []

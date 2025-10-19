#
# Created by Isai GORDEEV on 19/09/2025.
#

from abc import ABC, abstractmethod
from typing import Optional

from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class AbstractStage(ABC):
    metadata: "AbstractStageMetadata"

    def __init__(self, metadata: AbstractStageMetadata | None = None):
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
    ) -> tuple["SAXSSample", Optional[dict]]:
        """Override in subclass. Return (updated_sample,
        optional_metadata_dict)."""
        raise NotImplementedError

    def handle_metadata(
        self, sample: "SAXSSample", metadata: Optional[dict]
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

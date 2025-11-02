from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.metadata import FlowMetadata
from saxs.saxs.core.types.sample import ESAXSSampleKeys, SAXSSample
from saxs.saxs.processing.functions import moving_average


class FilterStage(IAbstractStage):
    def _process(self, sample: SAXSSample, flow_metadata: FlowMetadata):
        intensity = sample.get_intensity()

        filtered_intensity = moving_average(intensity, 10)
        sample[ESAXSSampleKeys.INTENSITY] = filtered_intensity

        return sample, flow_metadata

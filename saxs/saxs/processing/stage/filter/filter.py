from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.processing.functions import moving_average


class FilterStage(AbstractStage):
    def _process(self, stage_data):
        intensity = stage_data.get_intensity_array()

        filtered_intensity = moving_average(intensity, 10)

        return stage_data.set_intensity(filtered_intensity), None

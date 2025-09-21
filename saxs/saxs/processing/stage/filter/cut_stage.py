#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage


class CutStage(AbstractStage):
    def __init__(self, cut_point: int = 100):
        self.metadata = AbstractStageMetadata(data={"cut_point": cut_point})

    def _process(self, stage_data):
        cut_point = self.metadata.get("cut_point")
        _preprocessed_stage_data = (
            stage_data.set_q_values(stage_data.q_values[:cut_point])
            .set_intensity(stage_data.intensity[:cut_point])
            .set_intensity_error(stage_data.intensity_error[:cut_point])
        )

        return _preprocessed_stage_data, None

    def process(self, stage_data):
        return super().process(stage_data)

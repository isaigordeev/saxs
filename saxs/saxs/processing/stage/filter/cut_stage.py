#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_stage import AbstractStage


class CutStage(AbstractStage):
    def __init__(self, cut_point: int = 100):
        self.metadata = AbstractStageMetadata(values={"cut_point": cut_point})

    def _process(self, stage_data):
        cut_point = self.metadata.unwrap().get("cut_point")
        _preprocessed_stage_data = (
            stage_data.set_q_values(stage_data.get_q_values_array()[cut_point:])
            .set_intensity(stage_data.get_intensity_array()[cut_point:])
            .set_intensity_error(
                stage_data.get_intensity_error_array()[cut_point:]
            )
        )
        logger.info(
            f"init len {len(stage_data.get_intensity_array())} old len "
            f"{len(_preprocessed_stage_data.get_intensity_array())}"
        )
        return _preprocessed_stage_data, None

    def process(self, stage_data):
        return super().process(stage_data)

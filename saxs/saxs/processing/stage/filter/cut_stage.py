#
# Created by Isai GORDEEV on 20/09/2025.
#

from saxs.logging.logger import logger
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.types.stage_objects import AbstractStageMetadata


class CutStage(AbstractStage):
    def __init__(self, cut_point: int = 100):
        self.metadata = AbstractStageMetadata(values={"cut_point": cut_point})

    def _process(self, stage_data):
        cut_point = self.metadata.unwrap().get("cut_point")

        # Slice the data
        q_values_cut = stage_data.get_q_values_array()[cut_point:]
        intensity_cut = stage_data.get_intensity_array()[cut_point:]
        error_cut = stage_data.get_intensity_error_array()[cut_point:]

        _preprocessed_stage_data = (
            stage_data.set_q_values(q_values_cut)
            .set_intensity(intensity_cut)
            .set_intensity_error(error_cut)
        )

        # Log input/output info
        logger.info(
            f"\n=== CutStage Processing ===\n"
            f"Cut point:        {cut_point}\n"
            f"Input points:     {len(stage_data.get_q_values_array())}\n"
            f"Output points:    {len(q_values_cut)}\n"
            f"Q range (after):  [{min(q_values_cut)}, {max(q_values_cut)}]\n"
            f"Intensity range:  [{min(intensity_cut)}, {max(intensity_cut)}]\n"
            f"Error range:      [{min(error_cut)}, {max(error_cut)}]\n"
            f"=============================",
        )

        return _preprocessed_stage_data, None

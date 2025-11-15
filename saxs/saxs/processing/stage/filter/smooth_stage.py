import numpy as np

from saxs.saxs.core.stage.abstract_stage import IAbstractStage


class SmoothStage(IAbstractStage):
    def _process(self, stage_data):
        intensity = stage_data.get_intensity_array()

        new_intensity_state = np.maximum(intensity, 0)

        return stage_data.set_intensity(new_intensity_state), None

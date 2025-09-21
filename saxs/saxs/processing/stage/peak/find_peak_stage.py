#
# Created by Isai GORDEEV on 20/09/2025.
#

from scipy.signal import find_peaks

from saxs.logging.logger import logger
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.condition.abstract_condition import SampleCondition
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractConditionalStage,
)
from saxs.saxs.processing.stage.peak.process_peak_stage import ProcessPeakStage


class FindAllPeaksStage(AbstractConditionalStage):
    def __init__(
        self, chaining_stage: ProcessPeakStage, condition: SampleCondition
    ):
        super().__init__(chaining_stage, condition)

    def _process(self, stage_data):
        _params = {"x": stage_data.get_intensity_array()}

        # indices of peaks
        _peaks, _props = find_peaks(**_params)

        processed_stage_data = stage_data.set_metadata_dict({"peaks": _peaks})
        # self.metadata = AbstractStageMetadata(values={"peaks": _peaks})
        logger.info(f"peaks found {_peaks}")

        return processed_stage_data, {"peaks": _peaks}

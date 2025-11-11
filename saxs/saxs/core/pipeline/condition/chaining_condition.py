"""chaining_cond module.

Checks if there are remaining peaks.
"""

# Created by Isai Gordeev on 20/09/2025.

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition,
)
from saxs.saxs.core.stage.request.abst_request import EvalMetadata
from saxs.saxs.core.types.scheduler_metadata import ESchedulerRuntime


class ChainingPeakCondition(StageCondition):
    """Class predicat for evaluating chaining."""

    def __init__(self, key: str):
        self.key = key

    def evaluate(self, eval_metadata: EvalMetadata) -> bool:
        """
        Evaluate whether unprocessed peaks remain in metadata.

        This method checks the `EvalMetadata` container for
        entries in the `UNPROCESSED` field, which typically
        tracks peaks that have not yet been analyzed or chained.

        Parameters
        ----------
        eval_metadata : EvalMetadata
            Evaluation metadata object containing analysis state
            information, including lists of processed and
            unprocessed peaks.

        Returns
        -------
        bool
            `True` if there are unprocessed peaks remaining,
            otherwise `False`.
        """
        return (
            eval_metadata[EvalMetadata.Keys.CURRENT]
            != ESchedulerRuntime.UNDEFINED_PEAK.value
        )

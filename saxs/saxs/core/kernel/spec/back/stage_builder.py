from typing import Dict, List
from saxs.saxs.core.kernel.spec.stage_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractStage,
    AbstractRequestingStage,
)


class StageBuilder:
    """Builds stage instances from StageSpec objects without linking policies."""

    @staticmethod
    def build(stage_specs: List[StageSpec]) -> Dict[str, AbstractStage]:
        """
        Returns a dict: stage_id -> stage_instance
        """
        stage_instances: Dict[str, AbstractStage] = {}

        for spec in stage_specs:
            kwargs = spec.kwargs or {}

            if issubclass(spec.stage_cls, AbstractRequestingStage):
                instance = spec.stage_cls(metadata=kwargs, policy=None)
            else:
                instance = spec.stage_cls(**kwargs)

            stage_instances[spec.id] = instance

        return stage_instances

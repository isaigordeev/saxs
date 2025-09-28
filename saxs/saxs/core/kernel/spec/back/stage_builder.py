from typing import Dict, List
from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.runtime_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractStage,
    AbstractRequestingStage,
)


class StageBuilder:
    """Builds stage instances from StageSpec objects without linking policies."""

    @staticmethod
    def build(stage_specs: List[StageSpec]) -> Buffer[StageSpec]:
        """
        Returns a dict: stage_id -> stage_instance
        """
        stage_instances: Buffer[StageSpec] = Buffer[StageSpec]()

        for stage_spec in stage_specs:
            kwargs = stage_spec.kwargs or {}

            if issubclass(stage_spec.stage_cls, AbstractRequestingStage):
                instance = stage_spec.stage_cls(metadata=kwargs, policy=None)
            else:
                instance = stage_spec.stage_cls(**kwargs)

            stage_instances.register(stage_spec.id, instance)

        return stage_instances

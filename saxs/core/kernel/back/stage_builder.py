"""Stage builder: creates stage instances from StageSpec."""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import StageSpec
from saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.core.stage.abstract_stage import IAbstractStage


class StageBuilder:
    """Builds stage instances from StageSpec objects."""

    @staticmethod
    def build(stage_specs: Buffer[StageSpec]) -> Buffer[IAbstractStage]:
        """Create stage instances from specs."""
        stage_instances: Buffer[IAbstractStage] = Buffer()

        for stage_spec in stage_specs.values():
            metadata = stage_spec.metadata

            if issubclass(stage_spec.stage_cls, IAbstractRequestingStage):
                instance = stage_spec.stage_cls(metadata=metadata, policy=None)
            else:
                instance = stage_spec.stage_cls(metadata=metadata)

            stage_instances.register(stage_spec.id_, instance)

        return stage_instances

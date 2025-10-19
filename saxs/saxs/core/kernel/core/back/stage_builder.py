from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
    AbstractStage,
)


class StageBuilder:
    """Stage builder.

    Builds stage instances from StageSpec objects without linking
    policies.
    """

    @staticmethod
    def build(stage_specs: Buffer[StageSpec]) -> Buffer[AbstractStage]:
        """Return a dict: stage_id -> stage_instance."""
        stage_instances: Buffer[AbstractStage] = Buffer[AbstractStage]()

        for stage_spec in stage_specs.values():
            kwargs = stage_spec.kwargs or {}

            if issubclass(stage_spec.stage_cls, AbstractRequestingStage):
                instance = stage_spec.stage_cls(metadata=kwargs, policy=None)
            else:
                instance = stage_spec.stage_cls(**kwargs)

            stage_instances.register(stage_spec.id, instance)

        return stage_instances

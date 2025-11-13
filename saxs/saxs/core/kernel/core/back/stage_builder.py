"""Stage builder module.

This module provides the StageBuilder class, which is responsible for
instantiating AbstractStage objects from StageSpec specifications
during the kernel compilation process.

The builder creates stage instances with their associated metadata,
but does not perform the final linking of policies to requesting stages
(that is handled by StageLinker).

Classes
-------
StageBuilder
    Static builder class for creating stage instances from
    StageSpec objects.
"""

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
    IAbstractStage,
)


class StageBuilder:
    """Stage builder.

    Builds stage instances from StageSpec objects without linking
    policies.
    """

    @staticmethod
    def build(stage_specs: Buffer[StageSpec]) -> Buffer[IAbstractStage]:
        """Return a dict: stage_id -> stage_instance."""
        stage_instances: Buffer[IAbstractStage] = Buffer[IAbstractStage]()

        for stage_spec in stage_specs.values():
            metadata = stage_spec.metadata

            if issubclass(stage_spec.stage_cls, IAbstractRequestingStage):
                instance = stage_spec.stage_cls(metadata=metadata, policy=None)
            else:
                instance = stage_spec.stage_cls(metadata=metadata)

            stage_instances.register(stage_spec.id_, instance)

        return stage_instances

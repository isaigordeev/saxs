"""Stage linker module.

This module provides the StageLinker class, which is responsible for
linking ChainingPolicy instances to IAbstractRequestingStage
instances during the kernel compilation process.

The linker connects policies to stages based on the policy_id specified
in each StageSpec, enabling stages to conditionally request additional
stages during pipeline execution.

Classes
-------
StageLinker
    Static linker class for associating policies with requesting
    stage instances.
"""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import StageSpec
from saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class StageLinker:
    """Stage Linker class.

    Links policies and next-stage references
    to already built stage instances.
    """

    @staticmethod
    def link(
        stage_specs: Buffer[StageSpec],
        stage_instances: Buffer[IAbstractStage],
        policy_instances: Buffer[IAbstractChainingPolicy],
    ) -> Buffer[IAbstractStage]:
        for _stage_spec in stage_specs.values():
            if not issubclass(_stage_spec.stage_cls, IAbstractRequestingStage):
                continue

            _current_policy_id = _stage_spec.policy_id

            if not _current_policy_id:
                continue

            _stage: IAbstractRequestingStage = stage_instances.get(
                _stage_spec.id_,
            )

            _policy = policy_instances.get(_current_policy_id)

            _stage.policy = _policy

        return stage_instances

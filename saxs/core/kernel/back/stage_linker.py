"""Stage linker: connects policies to requesting stages."""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import StageSpec
from saxs.core.stage.abstract_cond_stage import IAbstractRequestingStage
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class StageLinker:
    """Links policies to requesting stage instances."""

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

            _stage = stage_instances.get(_stage_spec.id_)
            _policy = policy_instances.get(_current_policy_id)
            _stage.policy = _policy

        return stage_instances

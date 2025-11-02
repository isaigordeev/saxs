from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    IAbstractRequestingStage,
)
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class StageLinker:
    """Stage Linker class.

    Links policies and next-stage references
    to already built stage instances.
    """

    @staticmethod
    def link(
        stage_specs: Buffer[StageSpec],
        stage_instances: Buffer[IAbstractStage],
        policy_instances: Buffer[ChainingPolicy],
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

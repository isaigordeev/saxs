"""Policy linker: connects stage instances to policies."""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import PolicySpec
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class PolicyLinker:
    """Links policies with their pending stage references."""

    @staticmethod
    def link(
        policy_specs: Buffer[PolicySpec],
        stage_instances: Buffer[IAbstractStage],
        policy_instances: Buffer[IAbstractChainingPolicy],
    ) -> Buffer[IAbstractChainingPolicy]:
        for id_, _policy_spec in policy_specs.items():
            if not _policy_spec.pending_stages:
                continue

            next_stages: list[IAbstractStage] = []
            for next_id in _policy_spec.pending_stages:
                _stage = stage_instances.get(next_id)
                if _stage:
                    next_stages.append(_stage)

            if not next_stages:
                continue

            policy_instance = policy_instances.get(id_)
            if not policy_instance:
                continue
            policy_instance.pending_stages = next_stages

        return policy_instances

from typing import List

from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.runtime_spec import PolicySpec, StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
)
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class PolicyLinker:
    """Links policies and next-stage references to already built stage instances."""

    @staticmethod
    def link(
        policy_specs: Buffer[PolicySpec],
        stage_instances: Buffer[AbstractStage],
        policy_instances: Buffer[ChainingPolicy],
    ) -> Buffer[AbstractStage]:
        for id, _policy_spec in policy_specs.items():
            if not _policy_spec.next_stage_ids:
                continue

            # Resolve next stages
            next_stages = [
                stage_instances.get(next_id)
                for next_id in _policy_spec.next_stage_ids
            ]
            policy_instance: ChainingPolicy = policy_instances.get(id)
            policy_instance.next_stage_cls = next_stages

        return policy_instance

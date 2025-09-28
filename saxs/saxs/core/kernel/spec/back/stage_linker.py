from typing import List, Dict
from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.runtime_spec import PolicySpec, StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractStage,
    AbstractRequestingStage,
)


class StageLinker:
    """Links policies and next-stage references to already built stage instances."""

    @staticmethod
    def link(
        stage_specs: List[StageSpec], stage_instances: Buffer[StageSpec]
    ) -> Buffer[PolicySpec]:
        policy_buffer: Buffer[PolicySpec] = Buffer[PolicySpec]()

        for policy_spec in stage_specs:
            if not issubclass(policy_spec.stage_cls, AbstractRequestingStage):
                continue
            if not policy_spec.policy:
                continue

            # Instantiate the policy
            policy_kwargs = policy_spec.policy.condition_kwargs or {}
            condition_instance = None
            if policy_spec.policy.condition_cls:
                condition_instance = policy_spec.policy.condition_cls(
                    **policy_kwargs
                )

            policy_instance = policy_spec.policy.policy_cls(
                condition=condition_instance,
                next_stage_cls=None,  # will fill below
            )

            # Resolve next stages
            next_stages = [
                stage_instances[next_id]
                for next_id in policy_spec.policy.next_stage_ids or []
            ]
            policy_instance.next_stage = next_stages

            policy_buffer.register(policy_spec.id, policy_instance)

            # Attach policy to the stage
            stage_instances[policy_spec.id].policy = policy_instance

from typing import List, Dict
from saxs.saxs.core.kernel.spec.back.runtime_spec import StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractStage,
    AbstractRequestingStage,
)


class StageLinker:
    """Links policies and next-stage references to already built stage instances."""

    @staticmethod
    def link(
        stage_specs: List[StageSpec], stage_instances: Dict[str, AbstractStage]
    ):
        for spec in stage_specs:
            if not issubclass(spec.stage_cls, AbstractRequestingStage):
                continue
            if not spec.policy:
                continue

            # Instantiate the policy
            policy_kwargs = spec.policy.condition_kwargs or {}
            condition_instance = None
            if spec.policy.condition_cls:
                condition_instance = spec.policy.condition_cls(**policy_kwargs)

            policy_instance = spec.policy.policy_cls(
                condition=condition_instance,
                next_stage_cls=None,  # will fill below
            )

            # Resolve next stages
            next_stages = [
                stage_instances[next_id]
                for next_id in spec.policy.next_stage_ids or []
            ]
            policy_instance.next_stage = next_stages

            # Attach policy to the stage
            stage_instances[spec.id].policy = policy_instance

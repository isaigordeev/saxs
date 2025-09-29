from typing import Dict, List

from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.runtime_spec import PolicySpec, StageSpec
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
    AbstractStage,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class StageBuilder:
    """Builds stage instances from StageSpec objects without linking policies."""

    @staticmethod
    def build(stage_specs: Buffer[PolicySpec]) -> Buffer[ChainingPolicy]:
        """
        Returns a dict: stage_id -> stage_instance
        """
        policy_instances: Buffer[ChainingPolicy] = Buffer[ChainingPolicy]()

        for _, policy_spec in stage_specs.items():
            kwargs = policy_spec.kwargs or {}
            instance = policy_spec.policy_cls(**kwargs)

            policy_instances.register(policy_spec.id, instance)

        return policy_instances

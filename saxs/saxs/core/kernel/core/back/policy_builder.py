"""Policy builder module.

This module provides the PolicyBuilder class, which is responsible for
instantiating ChainingPolicy objects from PolicySpec specifications
during the kernel compilation process.

The builder creates policy instances with their associated conditions
and pending stage references, but does not perform the final linking
of policies to stage instances (that is handled by PolicyLinker).

Classes
-------
PolicyBuilder
    Static builder class for creating policy instances from
    PolicySpec objects.
"""

from typing import Any

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec
from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class PolicyBuilder:
    """Policy builder.

    Builds stage instances from StageSpec objects without linking
    policies.
    """

    @staticmethod
    def build(policy_specs: Buffer[PolicySpec]) -> Buffer[ChainingPolicy]:
        """Policy builder.

        Returns a dict: stage_id -> stage_instance.
        """
        policy_instances: Buffer[ChainingPolicy] = Buffer[ChainingPolicy]()

        for policy_spec in policy_specs.values():
            kwargs = PolicyBuilder.build_policy_kwargs(policy_spec)
            instance = policy_spec.policy_cls(**kwargs)

            policy_instances.register(policy_spec.id_, instance)

        return policy_instances

    @staticmethod
    def build_policy_kwargs(_policy_spec: PolicySpec) -> dict[str, Any]:
        _kwargs: dict[str, Any] = {}

        _kwargs["condition"] = PolicyBuilder.build_condition(_policy_spec)
        _kwargs["pending_stages"] = _policy_spec.pending_stages

        return _kwargs

    @staticmethod
    def build_condition(_policy_spec: PolicySpec) -> StageCondition:
        _kwargs: dict[str, Any] = {}
        _kwargs = _policy_spec.condition_kwargs
        return _policy_spec.condition(**_kwargs)

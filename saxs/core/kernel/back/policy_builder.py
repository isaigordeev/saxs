"""Policy builder: creates policy instances from PolicySpec."""

from typing import Any

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import PolicySpec
from saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class PolicyBuilder:
    """Builds policy instances from PolicySpec objects."""

    @staticmethod
    def build(
        policy_specs: Buffer[PolicySpec],
    ) -> Buffer[IAbstractChainingPolicy]:
        """Create policy instances from specs."""
        policy_instances: Buffer[IAbstractChainingPolicy] = Buffer()

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
        _kwargs = _policy_spec.condition_kwargs
        return _policy_spec.condition(**_kwargs)

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.front.declarative_specs import (
    PolicyDeclSpec,
    StageDeclSpec,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


@dataclass
class DeclarativePipeline:
    """
    Purely declarative pipeline:
    - stores ordered StageRefSpec
    - stores PolicyRefSpec separately
    """

    stages: List[StageDeclSpec] = field(default_factory=list)
    policies: Dict[str, PolicyDeclSpec] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "DeclarativePipeline":
        with open(yaml_str, "r") as f:
            data = yaml.safe_load(f)

        # Parse policies
        policy_spec_buffer: Buffer[PolicyDeclSpec] = Buffer[PolicyDeclSpec]()
        decl_policies: dict = data.get("policies", {})
        for _policy_decl_spec in decl_policies:
            _policy_decl_spec_obj = PolicyDeclSpec(
                id=_policy_decl_spec["id"],
                policy_cls=_policy_decl_spec["policy_cls"],
                condition_cls=_policy_decl_spec.get("condition_cls"),
                condition_kwargs=_policy_decl_spec.get("condition_kwargs", {}),
                next_stage_ids=_policy_decl_spec.get("next_stage_ids", []),
            )

            policy_spec_buffer.register(
                _policy_decl_spec["id"], _policy_decl_spec_obj
            )

        # Parse stages in order
        stages: List[StageDeclSpec] = []
        decl_stages: list = data.get("stages", [])

        for _stage_spec in decl_stages:
            _stage_decl_spec_obj = StageDeclSpec(
                id=_stage_spec["id"],
                stage_cls=_stage_spec["stage_cls"],
                kwargs=_stage_spec.get("kwargs", {}),
                policy_id=_stage_spec.get("policy_id"),
                before_ids=_stage_spec.get("before_ids", []),
                after_ids=_stage_spec.get("after_ids", []),
            )
            stages.append(_stage_decl_spec_obj)

        return cls(stages=stages, policies=policy_spec_buffer)

    def __str__(self) -> str:
        # Pretty print policies
        policies_str = (
            "\n".join(
                f"  - {pid}: {spec.policy_cls} (condition={spec.condition_cls}, next={spec.next_stage_ids})"
                for pid, spec in self.policies.items()
            )
            or "  <none>"
        )

        # Pretty print stages
        stages_str = (
            "\n".join(
                f"  - {s.id}: {s.stage_cls} (policy={s.policy_id}, before={s.before_ids}, after={s.after_ids})"
                for s in self.stages
            )
            or "  <none>"
        )

        return (
            "DeclarativePipeline:\n"
            f"Policies:\n{policies_str}\n"
            f"Stages:\n{stages_str}"
        )

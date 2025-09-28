from dataclasses import dataclass, field
from typing import Dict, List, Optional

import yaml

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
        data = yaml.safe_load(yaml_str)

        # Parse policies
        policies: Dict[str, PolicyDeclSpec] = {}
        for _policy_spec in data.get("policies", []):
            policies[_policy_spec["id"]] = PolicyDeclSpec(
                id=_policy_spec["id"],
                policy_cls=_policy_spec["policy_cls"],
                condition_cls=_policy_spec.get("condition_cls"),
                condition_kwargs=_policy_spec.get("condition_kwargs", {}),
                next_stage_ids=_policy_spec.get("next_stage_ids", []),
            )

        # Parse stages in order
        stages: List[StageDeclSpec] = []
        for _stage_spec in data.get("stages", []):
            stages.append(
                StageDeclSpec(
                    id=_stage_spec["id"],
                    stage_cls=_stage_spec["stage_cls"],
                    kwargs=_stage_spec.get("kwargs", {}),
                    policy_id=_stage_spec.get("policy_id"),
                    before_ids=_stage_spec.get("before_ids", []),
                    after_ids=_stage_spec.get("after_ids", []),
                )
            )

        return cls(stages=stages, policies=policies)

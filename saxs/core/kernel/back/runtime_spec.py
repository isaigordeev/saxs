"""Data models for stage and policy specifications."""

from dataclasses import dataclass, field
from typing import Any

from saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)

StageSpecId = str
PolicySpecId = str


@dataclass
class StageSpec:
    """Specification for a pipeline stage."""

    id_: StageSpecId
    stage_cls: type[IAbstractStage]
    metadata: Any = None
    kwargs: dict[str, Any] | None = None
    policy_id: PolicySpecId | None = None
    before: list[StageSpecId] | None = None
    after: list[StageSpecId] | None = None


@dataclass
class PolicySpec:
    """Specification for a chaining policy."""

    id_: PolicySpecId
    policy_cls: type[IAbstractChainingPolicy]
    condition: type[StageCondition]
    condition_kwargs: dict[str, Any] = field(default_factory=dict)
    pending_stages: list[StageSpecId] | None = None

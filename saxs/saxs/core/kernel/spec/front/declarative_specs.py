from dataclasses import dataclass
from typing import Any


@dataclass
class StageDeclSpec:
    id: str
    stage_cls: str  # string reference to stage class
    kwargs: dict[str, Any] | None = None
    policy_id: str | None = None  # string reference to policy
    before_ids: list[str] | None = None
    after_ids: list[str] | None = None


@dataclass
class PolicyDeclSpec:
    id: str
    policy_cls: str  # string reference to ChainingPolicy class
    condition_cls: str | None = None
    condition_kwargs: dict[str, Any] | None = None
    next_stage_ids: list[str] | None = None

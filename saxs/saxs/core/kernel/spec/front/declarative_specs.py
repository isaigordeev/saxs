from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StageDeclSpec:
    id: str
    stage_cls: str  # string reference to stage class
    kwargs: Optional[dict] = None
    policy_id: Optional[str] = None  # string reference to policy
    before_ids: Optional[List[str]] = None
    after_ids: Optional[List[str]] = None


@dataclass
class PolicyDeclSpec:
    id: str
    policy_cls: str  # string reference to ChainingPolicy class
    condition_cls: Optional[str] = None
    condition_kwargs: Optional[dict] = None
    next_stage_ids: Optional[List[str]] = None

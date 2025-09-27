from dataclasses import dataclass
from typing import List, Optional, Type, Union

from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


@dataclass
class PolicySpec:
    id: str
    policy_cls: Type[ChainingPolicy]
    condition_cls: Optional[Type] = None
    condition_kwargs: Optional[dict] = None
    next_stage_ids: Optional[List[str]] = None


@dataclass
class StageSpec:
    id: str
    stage_cls: Type[AbstractStage]
    kwargs: Optional[dict] = None
    metadata: Optional[dict] = None
    policy: Optional[PolicySpec] = None
    before: Optional[List["StageSpec"]] = None
    after: Optional[List["StageSpec"]] = None

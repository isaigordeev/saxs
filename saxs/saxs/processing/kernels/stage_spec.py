from dataclasses import dataclass
from typing import List, Optional, Type

from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


from dataclasses import dataclass
from typing import Optional, Type
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


from dataclasses import dataclass
from typing import Optional, Type, List, Union
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


@dataclass
class PolicySpec:
    policy_cls: Type[ChainingPolicy]
    condition_cls: Optional[Type] = None  # StageCondition class
    condition_args: Optional[List] = None  # Args for condition
    next_stage_id: Optional[str] = None  # Stage ID to inject next


@dataclass
class StageSpec:
    id: str
    stage_cls: Type[AbstractStage]
    kwargs: Optional[dict] = None
    policy: Optional[PolicySpec] = None
    metadata: Optional[dict] = None
    before_ids: Optional[List[str]] = None  # stage IDs to run before
    after_ids: Optional[List[str]] = None  # stage IDs to run after

    # After resolving references, you can populate these for runtime execution
    before: Optional[List["StageSpec"]] = None
    after: Optional[List["StageSpec"]] = None

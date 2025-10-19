"""Data models for defining stages and policies.

This module provides lightweight dataclasses that
describe how stages and policies are configured within
the SAXS (Small-Angle X-ray Scattering) pipeline.

Classes:
    PolicySpec: Defines how a chaining policy connects
    pipeline stages.
    StageSpec: Describes individual pipeline stages,
    their configuration, metadata, and ordering constraints.

These specifications are typically used by kernel builders
or schedulers to construct and organize SAXS processing
workflows dynamically.
"""

from dataclasses import dataclass
from typing import Any, List, Optional, Type

from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.stage.abstract_stage import (
    AbstractStage,
    AbstractStageMetadata,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


@dataclass
class PolicySpec:
    """Specification for defining a chaining policy.

    Attributes:
        id: Unique identifier for the policy.
        policy_cls: Class implementing the chaining logic.
        condition: Class defining the stage activation or transition condition.
        next_stage_ids: Optional list of stage IDs this policy connects to.
    """

    id: str
    policy_cls: Type[ChainingPolicy]
    condition: Type[StageCondition]
    next_stage_ids: Optional[List[str]] = None


@dataclass
class StageSpec:
    id: str
    stage_cls: Type[AbstractStage]
    kwargs: Optional[dict[str, Any]] = None
    metadata: Optional[AbstractStageMetadata] = None
    policy: Optional[str] = None
    before: Optional[List[str]] = None
    after: Optional[List[str]] = None

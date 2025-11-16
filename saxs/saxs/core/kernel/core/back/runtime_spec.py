"""Data models for defining stages and policies.

This module provides lightweight dataclasses that
describe how stages and policies are configured within
the SAXS (Small-Angle X-ray Scattering) pipeline.

Classes:
    PolicySpec: Defines how a chaining policy connects pipeline
    stages.
    StageSpec: Describes individual pipeline stages, their
    configuration, metadata, and ordering constraints.

These specifications are typically used by kernel builders
or schedulers to construct and organize SAXS processing
workflows dynamically.
"""

from dataclasses import dataclass, field
from typing import Any

from saxs.saxs.core.pipeline.condition.abstract_condition import StageCondition
from saxs.saxs.core.stage.abstract_stage import (
    IAbstractStage,
    TAbstractStageMetadata,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
    AbstractChainingPolicy,
)

StageSpecId = str
PolicySpecId = str


@dataclass
class StageSpec:
    """Specification for a pipeline stage in the SAXS workflow.

    Attributes
    ----------
        id: Unique identifier for the stage.
        stage_cls: Class implementing the stage behavior.
        kwargs: Optional keyword arguments used to
        instantiate the stage.
        metadata: Optional metadata associated with the stage.
        policy: Optional policy ID that governs stage chaining.
        before: Optional list of stage IDs that must precede
        this stage.
        after: Optional list of stage IDs that must follow
        this stage.
    """

    id_: StageSpecId
    stage_cls: type[IAbstractStage[Any]]
    metadata: TAbstractStageMetadata[Any, Any] | None = None
    kwargs: dict[str, Any] | None = None
    policy_id: PolicySpecId | None = None
    before: list[StageSpecId] | None = None
    after: list[StageSpecId] | None = None


@dataclass
class PolicySpec:
    """Specification for defining a chaining policy.

    Attributes
    ----------
        id: Unique identifier for the policy.
        policy_cls: Class implementing the chaining logic.
        condition: Class defining the stage activation or
        transition condition.
        next_stage_ids: Optional list of stage IDs
        this policy connects to.
    """

    id_: PolicySpecId
    policy_cls: type[AbstractChainingPolicy]
    condition: type[StageCondition]
    condition_kwargs: dict[str, Any] = field(default_factory=dict[str, Any])
    pending_stages: list[StageSpecId] | None = (
        None  # or default types and not vars
    )

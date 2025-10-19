"""
declaration_spec.py.

This module defines lightweight dataclass specifications used to
declare stages and policies within the SAXS (Small-Angle X-ray
Scattering) processing pipeline. These declarations serve as
metadata blueprints for dynamically constructing stages and policies
from string-based class references.

Classes
--------
StageDeclSpec
    Defines the specification for a stage declaration, including
    references to stage classes, policies, and ordering constraints.

PolicyDeclSpec
    Defines the specification for a policy declaration, including
    references to policy and condition classes and their associated
    configuration data.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class StageDeclSpec:
    """
    Specification for a stage declaration.

    This dataclass defines the metadata necessary to construct and
    order stages within a SAXS processing pipeline. It stores string
    references to stage classes and related policies, along with
    configuration arguments and dependency relationships.

    Attributes
    ----------
    id : str
        Unique identifier for the stage declaration.
    stage_cls : str
        String reference to the stage class to be instantiated.
    kwargs : dict of str to Any, optional
        Keyword arguments used to initialize the stage instance.
    policy_id : str, optional
        String reference to the policy associated with this stage.
    before_ids : list of str, optional
        List of stage IDs that this stage should precede.
    after_ids : list of str, optional
        List of stage IDs that this stage should follow.
    """

    id: str
    stage_cls: str  # string reference to stage class
    kwargs: dict[str, Any] | None = None
    policy_id: str | None = None  # string reference to policy
    before_ids: list[str] | None = None
    after_ids: list[str] | None = None


@dataclass
class PolicyDeclSpec:
    """
    Specification for a policy declaration.

    This dataclass defines the configuration required to construct a
    chaining or insertion policy used by the SAXS pipeline
    scheduler. It references both the policy and an optional
    condition class, along with any initialization parameters.

    Attributes
    ----------
    id : str
        Unique identifier for the policy declaration.
    policy_cls : str
        String reference to the policy class (e.g., chaining or
        insertion policy).
    condition_cls : str, optional
        String reference to an optional condition class that governs
        policy behavior.
    condition_kwargs : dict of str to Any, optional
        Keyword arguments for initializing the condition class.
    next_stage_ids : list of str, optional
        List of stage identifiers that the policy applies to next.
    """

    id: str
    policy_cls: str  # string reference to ChainingPolicy class
    condition_cls: str | None = None
    condition_kwargs: dict[str, Any] | None = None
    next_stage_ids: list[str] | None = None

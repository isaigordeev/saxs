"""
Module for registering stage and policy classes.

This module defines and populates registries for pipeline stages
and chaining policies used in SAXS data processing.
The `stage_registry` contains various processing stages, such as
filtering, background correction, and peak detection.
The `policy_registry` contains chaining policies that define how
stages are applied sequentially or conditionally.

The registries enable dynamic construction of processing pipelines
from configuration files or code, providing a type-safe and
bijective mapping between string identifiers and class objects.

Classes
-------
StageRegistry
    Registry for `AbstractStage` subclasses.
PolicyRegistry
    Registry for `ChainingPolicy` subclasses.

Instances
---------
stage_registry : StageRegistry
    Pre-populated registry of stage classes including CutStage,
    FilterStage, BackgroundStage, FindAllPeaksStage,
    and ProcessFitPeakStage.
policy_registry : PolicyRegistry
    Pre-populated registry of policy classes, currently containing
    SingleStageChainingPolicy.

Examples
--------
>>> from saxs.saxs.core.registry import stage_registry,
policy_registry
>>> stage_cls = stage_registry.get_class("FilterStage")
>>> stage_instance = stage_cls()
>>> policy_cls = policy_registry.get_class("ChainingPolicy")
>>> policy_instance = policy_cls()
"""

from typing import Any

from saxs.saxs.core.kernel.core.registry import (
    ClassRegistry,
    PolicyRegistry,
    StageRegistry,
)
from saxs.saxs.core.stage.abstract_stage import TStageMetadata
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.processing.stage.background.background import (
    BackgroundStage,
)
from saxs.saxs.processing.stage.cut.cut import CutStage
from saxs.saxs.processing.stage.filter.filter import FilterStage
from saxs.saxs.processing.stage.peak.find_peak import FindPeakStage
from saxs.saxs.processing.stage.peak.process_peak import (
    ProcessPeakStage,
)


def make_stage_registry() -> StageRegistry[TStageMetadata]:
    return ClassRegistry()


def make_policy_registry() -> PolicyRegistry:
    return ClassRegistry()


stage_registry: StageRegistry[Any] = make_stage_registry()
stage_registry.register("CutStage", CutStage)
stage_registry.register("FilterStage", FilterStage)
stage_registry.register("BackgroundStage", BackgroundStage)
stage_registry.register("FindAllPeaksStage", FindPeakStage)
stage_registry.register("ProcessFitPeakStage", ProcessPeakStage)

policy_registry: PolicyRegistry = make_policy_registry()
policy_registry.register(
    "SingleStageChainingPolicy",
    SingleStageChainingPolicy,
)

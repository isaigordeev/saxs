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

from saxs.saxs.core.kernel.spec.core.registry import (
    PolicyRegistry,
    StageRegistry,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.processing.stage.filter.background_stage import BackgroundStage
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)

stage_registry = StageRegistry()
stage_registry.register("CutStage", CutStage)
stage_registry.register("FilterStage", FilterStage)
stage_registry.register("BackgroundStage", BackgroundStage)
stage_registry.register("FindAllPeaksStage", FindAllPeaksStage)
stage_registry.register("ProcessFitPeakStage", ProcessFitPeakStage)

policy_registry: PolicyRegistry = PolicyRegistry()
policy_registry.register(
    "SingleStageChainingPolicy",
    SingleStageChainingPolicy,
)

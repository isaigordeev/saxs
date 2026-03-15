"""Kernel compiler and builders.

Transforms declarative pipeline specifications into fully
instantiated and linked stage and policy objects.
"""

from dataclasses import dataclass, field
from typing import Any

import yaml

from saxs.core.specs import Buffer, PolicySpec, StageSpec
from saxs.core.stage import (
    IAbstractChainingPolicy,
    IAbstractRequestingStage,
    IAbstractStage,
    StageCondition,
)


# ---------------------------------------------------------------------------
# Declarative specs (YAML frontend)
# ---------------------------------------------------------------------------


@dataclass
class StageDeclSpec:
    """Specification for a stage declaration."""

    id: str
    stage_cls: str
    kwargs: dict[str, Any] | None = None
    policy_id: str | None = None
    before_ids: list[str] | None = None
    after_ids: list[str] | None = None


@dataclass
class PolicyDeclSpec:
    """Specification for a policy declaration."""

    id: str
    policy_cls: str
    condition_cls: str | None = None
    condition_kwargs: dict[str, Any] | None = None
    next_stage_ids: list[str] | None = None


@dataclass
class DeclarativePipeline:
    """Purely declarative pipeline parsed from YAML."""

    stage_decl_specs: Buffer[StageDeclSpec] = field(default_factory=dict)
    policy_decl_specs: Buffer[PolicyDeclSpec] = field(default_factory=dict)
    order: list[StageDeclSpec] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "DeclarativePipeline":
        with open(yaml_str) as f:
            data = yaml.safe_load(f)

        # Parse policies
        policy_spec_buffer: Buffer[PolicyDeclSpec] = Buffer[PolicyDeclSpec]()
        decl_policies: dict = data.get("policies", {})
        for _policy_decl_spec in decl_policies:
            _policy_decl_spec_obj = PolicyDeclSpec(
                id=_policy_decl_spec["id"],
                policy_cls=_policy_decl_spec["policy_cls"],
                condition_cls=_policy_decl_spec.get("condition_cls"),
                condition_kwargs=_policy_decl_spec.get("condition_kwargs", {}),
                next_stage_ids=_policy_decl_spec.get("next_stage_ids", []),
            )
            policy_spec_buffer.register(
                _policy_decl_spec["id"], _policy_decl_spec_obj,
            )

        # Parse stages
        stage_spec_buffer: Buffer[StageDeclSpec] = Buffer[StageDeclSpec]()
        decl_stages: list = data.get("stages", [])

        for _stage_spec in decl_stages:
            _stage_decl_spec_obj = StageDeclSpec(
                id=_stage_spec["id"],
                stage_cls=_stage_spec["stage_cls"],
                kwargs=_stage_spec.get("kwargs", {}),
                policy_id=_stage_spec.get("policy_id"),
                before_ids=_stage_spec.get("before_ids", []),
                after_ids=_stage_spec.get("after_ids", []),
            )
            stage_spec_buffer.register(_stage_spec["id"], _stage_decl_spec_obj)

        order = data.get("pipeline", [])
        if not order:
            msg = "Order must be present in yaml file"
            raise ValueError(msg)

        return cls(
            stage_decl_specs=stage_spec_buffer,
            policy_decl_specs=policy_spec_buffer,
            order=order,
        )

    def __str__(self) -> str:
        policies_str = (
            "\n".join(
                f"  - {pid}: {spec.policy_cls} (condition={spec.condition_cls}, next={spec.next_stage_ids})"
                for pid, spec in self.policy_decl_specs.items()
            )
            or "  <none>"
        )
        stages_str = (
            "\n".join(
                f"  - {spec.id}: {spec.stage_cls} (policy={spec.policy_id}, before={spec.before_ids}, after={spec.after_ids})"
                for pid, spec in self.stage_decl_specs.items()
            )
            or "  <none>"
        )
        order_str = (
            "\n".join(
                f"  - {i} stage={order}" for i, order in enumerate(self.order)
            )
            or "  <none>"
        )
        return (
            "DeclarativePipeline:\n"
            f"Policies:\n{policies_str}\n"
            f"Stages:\n{stages_str}\n"
            f"Order:\n{order_str}"
        )


# ---------------------------------------------------------------------------
# Class registries (for YAML string -> class resolution)
# ---------------------------------------------------------------------------


class ClassRegistry:
    """Bijective registry mapping string identifiers to class objects."""

    def __init__(self) -> None:
        self._name_to_class: dict[str, type] = {}
        self._class_to_name: dict[type, str] = {}

    def register(self, name: str, cls_: type) -> None:
        if name in self._name_to_class:
            msg = f"Name '{name}' is already registered."
            raise ValueError(msg)
        if cls_ in self._class_to_name:
            msg = f"Class '{cls_.__name__}' is already registered."
            raise ValueError(msg)
        self._name_to_class[name] = cls_
        self._class_to_name[cls_] = name

    def get_class(self, name: str) -> type | None:
        return self._name_to_class.get(name)

    def get_name(self, cls: type) -> str | None:
        return self._class_to_name.get(cls)

    def from_yaml(self, name: str) -> type:
        cls = self.get_class(name)
        if cls is None:
            msg = f"Name '{name}' not registered in ClassRegistry."
            raise KeyError(msg)
        return cls


StageRegistry = ClassRegistry
PolicyRegistry = ClassRegistry


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


class StageBuilder:
    """Builds stage instances from StageSpec objects."""

    @staticmethod
    def build(stage_specs: Buffer[StageSpec]) -> Buffer[IAbstractStage]:
        """Create stage instances from specs."""
        stage_instances: Buffer[IAbstractStage] = Buffer()

        for stage_spec in stage_specs.values():
            metadata = stage_spec.metadata

            if issubclass(stage_spec.stage_cls, IAbstractRequestingStage):
                instance = stage_spec.stage_cls(metadata=metadata, policy=None)
            else:
                instance = stage_spec.stage_cls(metadata=metadata)

            stage_instances.register(stage_spec.id_, instance)

        return stage_instances


class PolicyBuilder:
    """Builds policy instances from PolicySpec objects."""

    @staticmethod
    def build(
        policy_specs: Buffer[PolicySpec],
    ) -> Buffer[IAbstractChainingPolicy]:
        """Create policy instances from specs."""
        policy_instances: Buffer[IAbstractChainingPolicy] = Buffer()

        for policy_spec in policy_specs.values():
            kwargs = PolicyBuilder.build_policy_kwargs(policy_spec)
            instance = policy_spec.policy_cls(**kwargs)
            policy_instances.register(policy_spec.id_, instance)

        return policy_instances

    @staticmethod
    def build_policy_kwargs(_policy_spec: PolicySpec) -> dict[str, Any]:
        _kwargs: dict[str, Any] = {}
        _kwargs["condition"] = PolicyBuilder.build_condition(_policy_spec)
        _kwargs["pending_stages"] = _policy_spec.pending_stages
        return _kwargs

    @staticmethod
    def build_condition(_policy_spec: PolicySpec) -> StageCondition:
        _kwargs = _policy_spec.condition_kwargs
        return _policy_spec.condition(**_kwargs)


# ---------------------------------------------------------------------------
# Linkers
# ---------------------------------------------------------------------------


class StageLinker:
    """Links policies to requesting stage instances."""

    @staticmethod
    def link(
        stage_specs: Buffer[StageSpec],
        stage_instances: Buffer[IAbstractStage],
        policy_instances: Buffer[IAbstractChainingPolicy],
    ) -> Buffer[IAbstractStage]:
        for _stage_spec in stage_specs.values():
            if not issubclass(_stage_spec.stage_cls, IAbstractRequestingStage):
                continue

            _current_policy_id = _stage_spec.policy_id
            if not _current_policy_id:
                continue

            _stage = stage_instances.get(_stage_spec.id_)
            _policy = policy_instances.get(_current_policy_id)
            _stage.policy = _policy

        return stage_instances


class PolicyLinker:
    """Links policies with their pending stage references."""

    @staticmethod
    def link(
        policy_specs: Buffer[PolicySpec],
        stage_instances: Buffer[IAbstractStage],
        policy_instances: Buffer[IAbstractChainingPolicy],
    ) -> Buffer[IAbstractChainingPolicy]:
        for id_, _policy_spec in policy_specs.items():
            if not _policy_spec.pending_stages:
                continue

            next_stages: list[IAbstractStage] = []
            for next_id in _policy_spec.pending_stages:
                _stage = stage_instances.get(next_id)
                if _stage:
                    next_stages.append(_stage)

            if not next_stages:
                continue

            policy_instance = policy_instances.get(id_)
            if not policy_instance:
                continue
            policy_instance.pending_stages = next_stages

        return policy_instances


# ---------------------------------------------------------------------------
# Compilers
# ---------------------------------------------------------------------------


class BaseCompiler:
    """Base compiler for building and linking pipeline components."""

    def build(
        self,
        stage_specs: Buffer[StageSpec],
        policy_specs: Buffer[PolicySpec],
    ) -> tuple[Buffer[IAbstractStage], Buffer[IAbstractChainingPolicy]]:
        """Build and link stage and policy instances from specs."""
        stage_instance: Buffer[IAbstractStage] = StageBuilder.build(
            stage_specs,
        )
        policy_instance: Buffer[IAbstractChainingPolicy] = PolicyBuilder.build(
            policy_specs,
        )

        PolicyLinker.link(
            policy_specs,
            stage_instance,
            policy_instance,
        )
        linked_stage_instance: Buffer[IAbstractStage] = StageLinker.link(
            stage_specs,
            stage_instance,
            policy_instance,
        )

        return linked_stage_instance, policy_instance


class YamlCompiler(BaseCompiler):
    """Compiler for YAML-based pipeline definitions."""

    @staticmethod
    def get_parser(
        path_to_yaml: str = "kernel.yaml",
    ) -> DeclarativePipeline:
        return DeclarativePipeline.from_yaml(path_to_yaml)

    def compile(self):
        _parser = self.get_parser()
        policy_decl_specs = _parser.policy_decl_specs
        stage_decl_specs = _parser.stage_decl_specs
        return self.build_from_decl(stage_decl_specs, policy_decl_specs)

    def build_from_decl(
        self,
        stage_decl_specs: Buffer[StageDeclSpec],
        policy_decl_specs: Buffer[PolicyDeclSpec],
    ) -> tuple[Buffer[IAbstractStage], Buffer[IAbstractChainingPolicy]]:
        """Compile from declarative specs to linked instances."""
        compiler = SpecCompiler()
        stage_specs = compiler.build_stage_specs(stage_decl_specs)
        policy_specs = compiler.build_policy_specs(policy_decl_specs)
        return self.build(stage_specs, policy_specs)


class SpecCompiler:
    """Builds runtime StageSpec and PolicySpec objects from declarative specs."""

    def __init__(
        self,
        stage_reg: StageRegistry | None = None,
        policy_reg: PolicyRegistry | None = None,
    ):
        # Lazy import to avoid circular dependency
        from saxs.core._registries import (
            policy_registry,
            stage_registry,
        )

        self.stage_registry: StageRegistry = stage_reg or stage_registry
        self.policy_registry: PolicyRegistry = policy_reg or policy_registry

    def build_policy_specs(
        self,
        policies_decl: Buffer[PolicyDeclSpec],
    ) -> Buffer[PolicySpec]:
        runtime_policies: Buffer[PolicySpec] = Buffer[PolicySpec]()

        for policy_id, policy_decl_spec in policies_decl.items():
            policy_cls = self.policy_registry.get_class(
                policy_decl_spec.policy_cls,
            )
            condition_cls = (
                self.stage_registry.get_class(policy_decl_spec.condition_cls)
                if policy_decl_spec.condition_cls
                else None
            )
            condition_kwargs = policy_decl_spec.condition_kwargs or {}
            next_stage_ids = policy_decl_spec.next_stage_ids or []

            _condition = (
                condition_cls(condition_kwargs) if condition_cls else None
            )

            policy = PolicySpec(
                id_=policy_decl_spec.id,
                policy_cls=policy_cls,
                condition=_condition,
                next_stage_ids=next_stage_ids,
            )
            runtime_policies.register(policy_id, policy)

        return runtime_policies

    def build_stage_specs(
        self,
        stages_decl: Buffer[StageDeclSpec],
    ) -> Buffer[StageSpec]:
        runtime_stages: Buffer[StageSpec] = Buffer[StageSpec]()

        for stage_decl_spec in stages_decl.values():
            stage_cls = self.stage_registry.get_class(
                stage_decl_spec.stage_cls,
            )

            if not stage_cls:
                continue

            policy_id = (
                stage_decl_spec.policy_id
                if stage_decl_spec.policy_id
                else None
            )

            stage_spec = StageSpec(
                id_=stage_decl_spec.id,
                stage_cls=stage_cls,
                kwargs=stage_decl_spec.kwargs or {},
                policy_id=policy_id,
                before=stage_decl_spec.before_ids or [],
                after=stage_decl_spec.after_ids or [],
            )
            runtime_stages.register(stage_decl_spec.id, stage_spec)

        return runtime_stages

    def build_pipeline(
        self,
        pipeline_decl: DeclarativePipeline,
    ) -> list[StageSpec]:
        """Build a runtime pipeline from declarative specs."""
        runtime_policies = self.build_policy_specs(
            pipeline_decl.policy_decl_specs,
        )
        runtime_stages = self.build_stage_specs(
            pipeline_decl.stage_decl_specs,
            runtime_policies,
        )
        return runtime_stages, runtime_policies


__all__ = [
    "BaseCompiler",
    "ClassRegistry",
    "DeclarativePipeline",
    "PolicyBuilder",
    "PolicyDeclSpec",
    "PolicyLinker",
    "PolicyRegistry",
    "SpecCompiler",
    "StageBuilder",
    "StageDeclSpec",
    "StageLinker",
    "StageRegistry",
    "YamlCompiler",
]

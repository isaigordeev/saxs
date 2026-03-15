"""Data models for stage and policy specifications, and generic buffer."""

from collections.abc import ItemsView, ValuesView
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from saxs.core.stage import IAbstractChainingPolicy, IAbstractStage, StageCondition

T = TypeVar("T")

StageSpecId = str
PolicySpecId = str


@dataclass
class StageSpec:
    """Specification for a pipeline stage."""

    id_: StageSpecId
    stage_cls: type[IAbstractStage]
    metadata: Any = None
    kwargs: dict[str, Any] | None = None
    policy_id: PolicySpecId | None = None
    before: list[StageSpecId] | None = None
    after: list[StageSpecId] | None = None


@dataclass
class PolicySpec:
    """Specification for a chaining policy."""

    id_: PolicySpecId
    policy_cls: type[IAbstractChainingPolicy]
    condition: type[StageCondition]
    condition_kwargs: dict[str, Any] = field(default_factory=dict)
    pending_stages: list[StageSpecId] | None = None


class Buffer(Generic[T]):
    """Generic registry for StageSpec or PolicySpec objects.

    Provides safe registration, lookup, and introspection.
    """

    def __init__(self):
        self._registry: dict[str, T] = {}

    def register(self, id_: str, item: T, *, overwrite: bool = False) -> None:
        """Register an item under a given ID."""
        if id_ in self._registry and not overwrite:
            msg = f"ID '{id_}' is already registered."
            raise KeyError(msg)
        self._registry[id_] = item

    def get(self, id_: str) -> T | None:
        """Retrieve the item by ID. Returns None if not found."""
        return self._registry.get(id_)

    def contains(self, id_: str) -> bool:
        """Check if an ID is already registered."""
        return id_ in self._registry

    def all_ids(self) -> list[str]:
        """Return a list of all registered IDs."""
        return list(self._registry.keys())

    def items(self) -> ItemsView[str, T]:
        """Return iterable of (ID, item) pairs."""
        return self._registry.items()

    def values(self) -> ValuesView[T]:
        """Return iterable of registered items."""
        return self._registry.values()

    def __str__(self) -> str:
        """Return a human-readable summary of the registry."""
        lines = [
            f"{self.__class__.__name__} with"
            f" {len(self._registry)} items:",
        ]
        for id_, item in self._registry.items():
            lines.append(
                f"  {id_}: {item.__class__.__name__},"
                f" attributes: {item.__dict__}",
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}({list(self._registry.keys())})"


# Aliases for clarity
StageRegistryBuffer = Buffer[StageSpec]
PolicyRegistryBuffer = Buffer[PolicySpec]


class KernelRegistry:
    """Creating kernel via registry."""

    def __init__(self):
        self.stage_specs: Buffer[StageSpec] = Buffer()
        self.policy_specs: Buffer[PolicySpec] = Buffer()
        self.execution_order: list[str] = []

    def register_stage(
        self, stage: StageSpec, *, initial: bool = True
    ) -> None:
        """Register stage.

        Parameters
        ----------
        stage : StageSpec
            The stage specification to register.
        initial : bool
            If True, add to execution_order (runs at pipeline start).
            If False, stage is only available for dynamic injection.
        """
        if self.stage_specs.contains(stage.id_):
            msg = f"Stage ID '{stage.id_}' is already registered."
            raise KeyError(msg)
        self.stage_specs.register(stage.id_, stage)
        if initial:
            self.execution_order.append(stage.id_)

    def register_policy(self, policy: PolicySpec) -> None:
        """Register policy."""
        self.policy_specs.register(policy.id_, policy)

    def pipeline(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
        """Return pipeline."""
        return self.stage_specs, self.policy_specs, self.execution_order


__all__ = [
    "Buffer",
    "KernelRegistry",
    "PolicyRegistryBuffer",
    "PolicySpec",
    "StageRegistryBuffer",
    "StageSpec",
    "StageSpecId",
    "PolicySpecId",
]

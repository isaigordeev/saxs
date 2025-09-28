from typing import Dict, Generic, Optional, TypeVar, Union
from saxs.saxs.core.kernel.spec.back.runtime_spec import StageSpec, PolicySpec

T = TypeVar("T", StageSpec, PolicySpec)


class Registry(Generic[T]):
    """
    Generic registry for StageSpec or PolicySpec objects.
    Provides safe registration, lookup, and introspection.
    """

    def __init__(self):
        self._registry: Dict[str, T] = {}

    def register(self, id: str, item: T, overwrite: bool = False):
        """
        Register an item under a given ID.
        Raises an error if the ID already exists and overwrite is False.
        """
        if id in self._registry and not overwrite:
            raise KeyError(f"ID '{id}' is already registered.")
        self._registry[id] = item

    def get(self, id: str) -> Optional[T]:
        """Retrieve the item by ID. Returns None if not found."""
        return self._registry.get(id)

    def contains(self, id: str) -> bool:
        """Check if an ID is already registered."""
        return id in self._registry

    def all_ids(self) -> list[str]:
        """Return a list of all registered IDs."""
        return list(self._registry.keys())

    def items(self):
        """Return iterable of (id, item) pairs."""
        return self._registry.items()


# Aliases for clarity
StageRegistryBuffer = Registry[StageSpec]
PolicyRegistryBuffer = Registry[PolicySpec]

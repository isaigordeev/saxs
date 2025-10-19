"""Generic typed registry buffers for SAXS pipeline.

This module defines a reusable, type-safe registry class
 (`Buffer`) that can store and manage SAXS pipeline specifications
such as `StageSpec` and `PolicySpec`.

Classes:
    Buffer: Generic registry for storing items keyed by unique
    string IDs.
    StageRegistryBuffer: Registry specialized for `StageSpec`
    objects.
    PolicyRegistryBuffer: Registry specialized for `PolicySpec`
    objects.
"""

from collections.abc import ItemsView, ValuesView
from typing import Generic, TypeVar

from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec, StageSpec

T = TypeVar("T")


class Buffer(Generic[T]):
    """
    Generic registry for StageSpec or PolicySpec objects.

    Provides safe registration, lookup, and introspection.
    """

    def __init__(self):
        self._registry: dict[str, T] = {}

    def register(self, id_: str, item: T, *, overwrite: bool = False) -> None:
        """
        Register an item under a given ID.

        Raises an error if the ID already exists and overwrite
        is False.
        """
        if id in self._registry and not overwrite:
            msg = f"ID '{id}' is already registered."
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
        """Return iterable of (ID, item) pairs.

        Returns
        -------
            A view of (ID, item) pairs stored in the registry.
        """
        return self._registry.items()

    def values(self) -> ValuesView[T]:
        """Return iterable of registered items.

        Returns
        -------
            A view of all registered objects.
        """
        return self._registry.values()

    def __str__(self) -> str:
        """Return a human-readable summary of the registry."""
        lines = [
            f"{self.__class__.__name__} of {T.__name__} with"
            "{len(self._registry)} items:",
        ]
        for id_, item in self._registry.items():
            lines.append(
                f"  {id_}: {item.__class__.__name__},"
                "attributes: {item.__dict__}",
            )
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}({list(self._registry.keys())})"


# Aliases for clarity
StageRegistryBuffer = Buffer[StageSpec]
PolicyRegistryBuffer = Buffer[PolicySpec]

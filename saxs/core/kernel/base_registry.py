"""Registry module for mapping string identifiers to class objects."""

from typing import Generic, TypeVar

from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)

T = TypeVar("T")


class ClassRegistry(Generic[T]):
    """Bijective registry mapping string identifiers to class objects."""

    def __init__(self) -> None:
        self._name_to_class: dict[str, type[T]] = {}
        self._class_to_name: dict[type[T], str] = {}

    def register(self, name: str, cls_: type[T]) -> None:
        if name in self._name_to_class:
            msg = f"Name '{name}' is already registered."
            raise ValueError(msg)
        if cls_ in self._class_to_name:
            msg = f"Class '{cls_.__name__}' is already registered."
            raise ValueError(msg)
        self._name_to_class[name] = cls_
        self._class_to_name[cls_] = name

    def get_class(self, name: str) -> type[T] | None:
        return self._name_to_class.get(name)

    def get_name(self, cls: type[T]) -> str | None:
        return self._class_to_name.get(cls)

    def from_yaml(self, name: str) -> type[T]:
        cls = self.get_class(name)
        if cls is None:
            msg = f"Name '{name}' not registered in ClassRegistry."
            raise KeyError(msg)
        return cls


StageRegistry = ClassRegistry[IAbstractStage]
PolicyRegistry = ClassRegistry[IAbstractChainingPolicy]

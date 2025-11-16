"""
Registry module.

This module provides a generic and type-safe registry system for
mapping string identifiers to class objects in the SAXS processing
pipeline. It allows registering and retrieving classes in a
bijective manner, meaning each string identifier uniquely maps to
a single class and vice versa.

Classes
-------
ClassRegistry
    A generic registry for bijective mapping between string names
    and class objects.
StageRegistry
    Specialized registry for AbstractStage subclasses.
PolicyRegistry
    Specialized registry for ChainingPolicy subclasses.

Functions
---------
Optional listing of module-level functions.

Examples
--------
>>> from saxs.saxs.core.stage.registry import StageRegistry,
PolicyRegistry
>>> stage_registry = StageRegistry()
>>> stage_registry.register("MyStage", MyStage)
>>> stage_registry.get_class("MyStage")
<class 'MyStage'>

Notes
-----
- This module uses Python generics (TypeVar, Generic) to ensure
type safety.
- Designed to integrate with YAML-based deserialization workflows.
"""

from typing import Generic, TypeVar

from saxs.saxs.core.stage.abstract_stage import IAbstractStage, TStageMetadata
from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
    AbstractChainingPolicy,
)

# Generic type variable for classes that can be registered.
T = TypeVar("T")


class ClassRegistry(Generic[T]):
    """ClassRegistry.

    A bijective registry mapping string identifiers to class
    objects.

    This registry allows registering classes (such as
    `AbstractStage` or `ChainingPolicy` subclasses) under unique
    string names and retrieving them in both directions
    (name → class or class → name).

    Examples
    --------
        >>> registry = ClassRegistry()
        >>> registry.register("MyStage", MyStage)
        >>> registry.get_class("MyStage")
        <class 'MyStage'>
        >>> registry.get_name(MyStage)
        'MyStage'

    Attributes
    ----------
        _name_to_class (Dict[str, Type[T]]): Maps string names to
        class objects.
        _class_to_name (Dict[Type[T], str]): Maps class objects to
        their string names.
    """

    def __init__(self) -> None:
        self._name_to_class: dict[str, type[T]] = {}
        self._class_to_name: dict[type[T], str] = {}

    def register(self, name: str, cls_: type[T]) -> None:
        """
        Register a class under a unique string identifier.

        Parameters
        ----------
            name: The unique string identifier for the class.
            cls: The class object to register.

        Raises
        ------
            ValueError: If the name or class is already
            registered.
        """
        if name in self._name_to_class:
            msg = f"Name '{name}' is already registered."
            raise ValueError(msg)
        if cls_ in self._class_to_name:
            msg = f"Class '{cls_.__name__}' is already registered."
            raise ValueError(msg)

        self._name_to_class[name] = cls_
        self._class_to_name[cls_] = name

    def get_class(self, name: str) -> type[T] | None:
        """
        Retrieve the class object associated with a given name.

        Parameters
        ----------
            name: The string identifier of the class.

        Returns
        -------
            The class object if found, otherwise None.
        """
        return self._name_to_class.get(name)

    def get_name(self, cls: type[T]) -> str | None:
        """Get name func.

        Retrieve the registered name associated with a given class
        object.

        Parameters
        ----------
            cls: The class object to look up.

        Returns
        -------
            The registered string name if found, otherwise None.
        """
        return self._class_to_name.get(cls)

    def from_yaml(self, name: str) -> type[T]:
        """
        Retrieve a class object by its name, raising if not found.

        This method is intended for deserialization workflows
        (e.g., when constructing objects from YAML configuration).

        Parameters
        ----------
            name: The string identifier to look up.

        Returns
        -------
            The class object corresponding to the given name.

        Raises
        ------
            KeyError: If the name is not registered.
        """
        cls = self.get_class(name)
        if cls is None:
            msg = f"Name '{name}' not registered in ClassRegistry."
            raise KeyError(msg)
        return cls


# ------------------------
# Aliases for clarity
# ------------------------
StageRegistry = ClassRegistry[IAbstractStage[TStageMetadata]]
PolicyRegistry = ClassRegistry[AbstractChainingPolicy]

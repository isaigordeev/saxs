from dataclasses import dataclass, field
from typing import Type, Dict, Optional, Union
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
    AbstractStage,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


@dataclass
class ClassRegistry:
    """
    Generic bijective registry for stages or policies.
    Maps string identifiers <-> class objects.
    """

    _name_to_class: Dict[str, Type] = field(default_factory=dict)
    _class_to_name: Dict[Type, str] = field(default_factory=dict)

    def __init__(self, initial_mapping: Optional[Dict[str, Type]] = None):
        self._name_to_class = {}
        self._class_to_name = {}
        if initial_mapping:
            for name, cls in initial_mapping.items():
                self.register(name, cls)

    def register(self, name: str, cls: Type):
        """Register a class with a unique string identifier."""
        if name in self._name_to_class:
            raise ValueError(f"Name '{name}' is already registered.")
        if cls in self._class_to_name:
            raise ValueError(f"Class '{cls.__name__}' is already registered.")

        self._name_to_class[name] = cls
        self._class_to_name[cls] = name

    def get_class(self, name: str) -> Optional[Type]:
        """Return the class for a given string identifier."""
        return self._name_to_class.get(name)

    def get_name(self, cls: Type) -> Optional[str]:
        """Return the string identifier for a given class."""
        return self._class_to_name.get(cls)

    def from_yaml(self, name: str) -> Type:
        """Return the class for a YAML string. Raises KeyError if not found."""
        cls = self.get_class(name)
        if cls is None:
            raise KeyError(f"Name '{name}' not registered in ClassRegistry.")
        return cls


# ------------------------
# Aliases for clarity
# ------------------------
StageRegistry = (
    ClassRegistry  # expects AbstractStage / AbstractRequestingStage subclasses
)
PolicyRegistry = ClassRegistry  # expects ChainingPolicy subclasses

"""Abstract base class for SAXS kernels.

This module defines the `IAbstractKernel` class, which provides
an abstract interface for SAXS (Small-Angle X-ray Scattering)
kernel implementations.

Classes derived from `IAbstractKernel` are responsible for:
- Creating a `SAXSSample` instance.
- Defining the pipeline stages and policies.
- Building and submitting the pipeline to a scheduler.
"""

from abc import ABC, abstractmethod

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import PolicySpec, StageSpec


class IAbstractKernel(ABC):
    """Abstract kernel class for SAXS pipeline.

    Defines the core interface that all SAXS kernel
    implementations must follow.
    """

    @abstractmethod
    def define(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
        """Define pipeline.

        Define which stages and policies form
        the entrypoint pipeline.
        """

    @abstractmethod
    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""

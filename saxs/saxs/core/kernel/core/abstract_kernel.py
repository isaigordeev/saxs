"""Abstract base class for SAXS kernels.

This module defines the `AbstractKernel` class, which provides
an abstract interface for SAXS (Small-Angle X-ray Scattering)
kernel implementations.

Classes derived from `AbstractKernel` are responsible for:
- Creating a `SAXSSample` instance.
- Defining the pipeline stages and policies.
- Building and submitting the pipeline to a scheduler.
"""

from abc import ABC, abstractmethod

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec, StageSpec


class AbstractKernel(ABC):
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

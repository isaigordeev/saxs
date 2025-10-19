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
from typing import TYPE_CHECKING, Any, List

from saxs.saxs.core.kernel.spec.back.buffer import Buffer

if TYPE_CHECKING:
    from saxs.saxs.core.data.sample import SAXSSample


class AbstractKernel(ABC):
    """Abstract kernel class.

    Defines the core interface that all SAXS kernel
    implementations must follow.
    """

    @abstractmethod
    def create_sample(self) -> "SAXSSample":
        """Build sample."""

    @abstractmethod
    def define(self) -> None:
        """Define pipeline.

        Define which stages and policies form
        the entrypoint pipeline.
        """

    @abstractmethod
    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""

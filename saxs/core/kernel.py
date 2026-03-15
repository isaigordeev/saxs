"""Base kernel: orchestrates pipeline construction and execution."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from saxs.core.compiler import BaseCompiler
from saxs.core.pipeline import Pipeline
from saxs.core.specs import Buffer, PolicySpec, StageSpec
from saxs.core.stage import IAbstractStage
from saxs.core.types import SAXSSample

if TYPE_CHECKING:
    from saxs.core.scheduler import IAbstractScheduler
    from saxs.core.stage import IAbstractChainingPolicy


class IAbstractKernel(ABC):
    """Abstract kernel class for SAXS pipeline."""

    @abstractmethod
    def define(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
        """Define which stages and policies form the entrypoint pipeline."""

    @abstractmethod
    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""


class BaseKernel(IAbstractKernel):
    """Orchestrates pipeline building, scheduler wiring, and execution."""

    def __init__(self, scheduler: "IAbstractScheduler"):
        self.scheduler = scheduler
        self.execution_order: list[str] = []
        self.build()

    def build(self) -> None:
        """Build entry stages and submit them to scheduler."""
        _stage_decl, _policy_decl, _execution_order = self.define()

        _comp = BaseCompiler()

        self.stage_buffer: Buffer[IAbstractStage]
        self.policy_buffer: Buffer[IAbstractChainingPolicy]

        self.stage_buffer, self.policy_buffer = _comp.build(
            _stage_decl,
            _policy_decl,
        )

        _initial_stages = self._get_initial_stage(_execution_order)

        self.pipeline = Pipeline.with_stages(
            _initial_stages,
            scheduler=self.scheduler,
        )

    def _get_initial_stage(
        self,
        _execution_order: list[str],
    ) -> list[IAbstractStage]:
        """Get initial stages in execution order."""
        _initial_stages: list[IAbstractStage] = []
        for _stage_id in _execution_order:
            _stage = self.stage_buffer.get(_stage_id)
            if _stage:
                _initial_stages.append(_stage)
        return _initial_stages

    def run(self, init_sample: SAXSSample) -> SAXSSample:
        """Run the kernel pipeline on the given sample."""
        return self.pipeline.run(init_sample)


__all__ = [
    "BaseKernel",
    "IAbstractKernel",
]

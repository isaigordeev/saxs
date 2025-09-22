from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Union

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.pipeline.pipeline import Pipeline
from saxs.saxs.core.pipeline.scheduler.scheduler import AbstractScheduler
from saxs.saxs.core.stage.abstract_cond_stage import AbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.policy.policy_registry import PolicyRegistry
from saxs.saxs.core.stage.request.abst_request import StageRequest


def build_initial_stages(
    stage_defs: List[
        Union[
            Type["AbstractStage"],
            Tuple[Type["AbstractRequestingStage"], "ChainingPolicy"],
        ]
    ],
    registry: PolicyRegistry,
) -> List["AbstractStage"]:
    """
    Build all initial stages.

    Rules:
    - Plain AbstractStage → append as is.
    - AbstractRequestingStage without a tuple → append and register default policy.
    - Tuple(AbstractRequestingStage, ChainingPolicy) → append and register given policy.
    """
    stages = []

    for entry in stage_defs:
        # Case 1: plain stage
        if isinstance(entry, type) and issubclass(entry, AbstractStage):
            if issubclass(entry, AbstractRequestingStage):
                # Register default policy if not already registered
                default_policy = entry.default_policy()
                registry.register(entry, default_policy)
                stages.append(entry(default_policy))
            else:
                stages.append(entry())
            continue

        # Case 2: requesting stage with explicit policy
        if isinstance(entry, tuple) and len(entry) == 2:
            stage_cls, policy = entry
            if not issubclass(stage_cls, AbstractRequestingStage):
                raise TypeError(
                    f"{stage_cls.__name__} does not accept a policy"
                )
            # registry.register(stage_cls, policy) # do not registers stages
            stages.append(stage_cls(policy))
            continue

        raise TypeError(f"Invalid stage definition: {entry}")

    return stages


class AbstractKernel(ABC):
    """
    Encapsulates orchestration of:
    - pipeline building
    - scheduler wiring
    - sample creation
    """

    def __init__(self, scheduler: "AbstractScheduler", scheduler_policy):
        self.scheduler = scheduler
        self.registry = PolicyRegistry()
        self.scheduler_policy = scheduler_policy

    @abstractmethod
    def create_sample(self, *args, **kwargs) -> "SAXSSample":
        """Factory for building a sample."""
        pass

    @abstractmethod
    def pipeline_definition(
        self,
    ) -> List[
        Union[
            Type["AbstractStage"],
            Tuple[Type["AbstractRequestingStage"], "ChainingPolicy"],
        ]
    ]:
        """Define which stages and policies form the entrypoint pipeline."""
        pass

    def build_pipeline(self, sample: "SAXSSample"):
        """Build entry stages and submit them to scheduler."""
        stage_defs = self.pipeline_definition()
        initial_stages = build_initial_stages(stage_defs, self.registry)

        self.pipeline = Pipeline.with_stages(*initial_stages, self.scheduler)

    def run(self):
        """Run the scheduler until pipeline is complete."""
        return self.pipeline.run()

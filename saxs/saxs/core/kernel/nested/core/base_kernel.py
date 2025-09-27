from saxs.logging.logger import logger
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    InsertionPolicy,
    SaturationInsertPolicy,
)
from saxs.saxs.core.pipeline.scheduler.scheduler import AbstractScheduler
from saxs.saxs.core.stage.abstract_cond_stage import AbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.stage.policy.policy_registry import PolicyRegistry
from saxs.saxs.processing.kernel.nested.core.abstract_kernel import (
    AbstractKernel,
)


from typing import Any, Dict, List, Tuple, Type, Union


class BaseKernel(AbstractKernel):
    """
    Encapsulates orchestration of:
    - pipeline building
    - scheduler wiring
    - sample creation
    """

    def __init__(
        self,
        scheduler: "AbstractScheduler",
        scheduler_policy: InsertionPolicy,
    ):
        self.scheduler = scheduler
        self.registry = PolicyRegistry()
        self.scheduler_policy = scheduler_policy or SaturationInsertPolicy()

    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    @staticmethod
    def build_initial_stages(
        stage_defs: List[
            Union[
                Type["AbstractStage"],
                Tuple[Type["AbstractStage"], Dict[str, Any], "ChainingPolicy"],
                Tuple[Type["AbstractStage"], Dict[str, Any]],
            ]
        ],
        registry: "PolicyRegistry",
    ) -> List["AbstractStage"]:
        """
        Build all initial stages with optional kwargs and logging.

        Rules:
        - Plain AbstractStage → append as is.
        - AbstractRequestingStage without a tuple → append and register default policy.
        - Tuple(StageClass, kwargs_dict[, policy]) → append stage using kwargs.
        """
        stages = []

        for idx, entry in enumerate(stage_defs, start=1):
            # Case 1: plain stage class
            if isinstance(entry, type) and issubclass(entry, AbstractStage):
                if issubclass(entry, AbstractRequestingStage):
                    default_policy = entry.default_policy()
                    registry.register(entry, default_policy)
                    stages.append(entry(default_policy))
                    logger.info(
                        f"[{idx}] Built requesting stage {entry.__name__} with default policy {default_policy.__class__.__name__}"
                    )
                else:
                    stages.append(entry())
                    logger.info(f"[{idx}] Built plain stage {entry.__name__}")
                continue

            # Case 2: stage class with kwargs, optional policy
            if isinstance(entry, tuple) and 2 <= len(entry) <= 3:
                stage_cls = entry[0]
                kwargs = entry[1]
                policy = entry[2] if len(entry) == 3 else None

                if issubclass(stage_cls, AbstractRequestingStage):
                    actual_policy = policy or stage_cls.default_policy()
                    registry.register(stage_cls, actual_policy)
                    stages.append(
                        stage_cls(metadata=kwargs, policy=actual_policy)
                    )
                    logger.info(
                        f"[{idx}] Built requesting stage {stage_cls.__name__} with policy {actual_policy.__class__.__name__} and kwargs {kwargs}"
                    )
                else:
                    stages.append(stage_cls(**kwargs))
                    logger.info(
                        f"[{idx}] Built plain stage {stage_cls.__name__} with kwargs {kwargs}"
                    )
                continue

            raise TypeError(f"Invalid stage definition at index {idx}: {entry}")

        logger.info(f"Total stages built: {len(stages)}")
        return stages

from typing import Dict, List, Optional, Type

from saxs.saxs.core.data.stage_objects import AbstractStageMetadata
from saxs.saxs.core.stage.abstract_cond_stage import AbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class CompositeStage(AbstractStage):
    """
    Wraps a main stage class and optional 'before' and 'after' stage classes.
    All stages are instantiated when the CompositeStage is created.
    """

    def __init__(
        self,
        main_stage_cls: Type[AbstractStage],
        main_kwargs: Optional[Dict] = None,
        before: Optional[List[Type[AbstractStage]]] = None,
        after: Optional[List[Type[AbstractStage]]] = None,
        policy: Optional[ChainingPolicy] = None,
        metadata: Optional[AbstractStageMetadata] = None,
    ):
        super().__init__(metadata)
        self.main_kwargs = main_kwargs or {}
        self.policy = policy

        # Instantiate main stage
        if issubclass(main_stage_cls, AbstractRequestingStage):
            self.main_stage = main_stage_cls(
                policy=self.policy, **self.main_kwargs
            )
        else:
            self.main_stage = main_stage_cls(**self.main_kwargs)

        # Instantiate before/after stages
        self.before = [cls() for cls in (before or [])]
        self.after = [cls() for cls in (after or [])]

    def _process(self, sample):
        for stage in self.before:
            sample = stage.process(sample)

        # main stage
        sample = self.main_stage.process(sample)

        for stage in self.after:
            sample = stage.process(sample)
        return sample, getattr(self.main_stage, "metadata", None)

    def request_stage(self):
        """Delegate request to main stage if it is requesting."""
        if isinstance(self.main_stage, AbstractRequestingStage):
            return self.main_stage.request_stage()
        return []

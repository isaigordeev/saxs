from saxs.saxs.core.stage.abstract_cond_stage import IAbstractRequestingStage
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


class CompositeRequstingStage(IAbstractRequestingStage):
    """CompositeRequstingStage.

    Wraps a main stage class and optional 'before' and 'after' stage
    classes. All stages are instantiated when the CompositeStage
    is created.
    """

    def __init__(
        self,
        main_stage_cls: type[IAbstractStage],
        main_kwargs: dict | None = None,
        before: list[type[IAbstractStage]] | None = None,
        after: list[type[IAbstractStage]] | None = None,
        policy: ChainingPolicy | None = None,
        metadata: TAbstractStageMetadata | None = None,
    ):
        super().__init__(metadata)
        self.main_kwargs = main_kwargs or {}
        self.policy = policy

    def _process(self, sample):
        for stage in self.before:
            sample = stage.process(sample)

        # main stage
        sample = self.main_stage.process(sample)

        for stage in self.after:
            sample = stage.process(sample)
        return sample, getattr(self.main_stage, "metadata", None)

    def build(self):
        return self._build()

    def _build(self) -> None:
        # Instantiate main stage
        self.main_stage = self.main_stage_cls(
            policy=self.policy,
            **self.main_kwargs,
        )

        # Instantiate before/after stages
        self.before = [cls() for cls in (self.before or [])]
        self.after = [cls() for cls in (self.after or [])]

    def request_stage(self):
        """Delegate request to main stage if it is requesting."""
        if isinstance(self.main_stage, IAbstractRequestingStage):
            return self.main_stage.request_stage()
        return []

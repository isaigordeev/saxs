from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saxs.saxs.core.stage.abstract_cond_stage import (
        IAbstractRequestingStage,
    )
    from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
        ChainingPolicy,
    )


class PolicyRegistry:
    """
    Keeps track of which ChainingPolicy belongs to which RequestingStage type.
    Acts as a factory when stages are created dynamically.
    """

    def __init__(self):
        self._policies = {}

    def register(
        self,
        stage_cls: type["IAbstractRequestingStage"],
        policy: "ChainingPolicy",
    ) -> None:
        self._policies[stage_cls] = policy

    def get_policy(
        self,
        stage_cls: type["IAbstractRequestingStage"],
    ) -> "ChainingPolicy":
        if stage_cls not in self._policies:
            msg = f"No policy registered for {stage_cls.__name__}"
            raise ValueError(msg)
        return self._policies[stage_cls]

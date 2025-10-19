"""Interface to manage Buffers."""

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec, StageSpec


class KernelRegistry:
    """Creating kernel via registry."""

    def __init__(self):
        self.stage_specs: Buffer[StageSpec] = Buffer()
        self.policy_specs: Buffer[PolicySpec] = Buffer()
        self.execution_order: list[
            str
        ] = []  # Explicit memorized order of stage IDs

    def register_stage(self, stage: StageSpec) -> None:
        """Register stage."""
        if self.stage_specs.contains(stage.id):
            msg = f"Stage ID '{stage.id}' is already registered."
            raise KeyError(msg)
        self.stage_specs.register(stage.id, stage)
        self.execution_order.append(
            stage.id,
        )  # Memorize the order of registration

    def register_policy(self, policy: PolicySpec) -> None:
        """Register policy."""
        self.policy_specs.register(policy.id, policy)

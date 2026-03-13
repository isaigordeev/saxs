"""Interface to manage Buffers."""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.runtime_spec import PolicySpec, StageSpec


class KernelRegistry:
    """Creating kernel via registry."""

    def __init__(self):
        self.stage_specs: Buffer[StageSpec] = Buffer()
        self.policy_specs: Buffer[PolicySpec] = Buffer()
        self.execution_order: list[
            str
        ] = []  # Explicit memorized order of stage IDs

    def register_stage(
        self, stage: StageSpec, *, initial: bool = True
    ) -> None:
        """Register stage.

        Parameters
        ----------
        stage : StageSpec
            The stage specification to register.
        initial : bool
            If True, add to execution_order (runs at pipeline start).
            If False, stage is only available for dynamic injection.
        """
        if self.stage_specs.contains(stage.id_):
            msg = f"Stage ID '{stage.id_}' is already registered."
            raise KeyError(msg)
        self.stage_specs.register(stage.id_, stage)
        if initial:
            self.execution_order.append(stage.id_)

    def register_policy(self, policy: PolicySpec) -> None:
        """Register policy."""
        self.policy_specs.register(policy.id_, policy)

    def pipeline(
        self,
    ) -> tuple[Buffer[StageSpec], Buffer[PolicySpec], list[str]]:
        """Return pipeline."""
        return self.stage_specs, self.policy_specs, self.execution_order

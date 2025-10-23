from typing import TYPE_CHECKING

from saxs.saxs.core.kernel.core._define_registry import (
    policy_registry,
    stage_registry,
)
from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec, StageSpec
from saxs.saxs.core.kernel.core.front.declarative_specs import (
    PolicyDeclSpec,
    StageDeclSpec,
)

if TYPE_CHECKING:
    from saxs.saxs.core.kernel.core.front.parser import DeclarativePipeline
    from saxs.saxs.core.kernel.core.registry import (
        PolicyRegistry,
        StageRegistry,
    )


class SpecCompiler:
    """SpecCompiler.

    Builds runtime StageSpec and PolicySpec objects from purely
    declarative specs.
    - Resolves string references to classes using StageRegistry
    and PolicyRegistry.
    - Keeps policy and stage building logically separated but in
    one class.
    """

    def __init__(
        self,
        stage_registry: "StageRegistry" = stage_registry,
        policy_registry: "PolicyRegistry" = policy_registry,
    ):
        self.stage_registry: StageRegistry = stage_registry
        self.policy_registry: PolicyRegistry = policy_registry

    # --------------------------
    # Policy building
    # --------------------------
    def build_policy_specs(
        self,
        policies_decl: Buffer[PolicyDeclSpec],
    ) -> Buffer[PolicySpec]:
        runtime_policies: Buffer[PolicySpec] = Buffer[PolicySpec]()

        for policy_id, policy_decl_spec in policies_decl.items():
            policy_cls = self.policy_registry.get_class(
                policy_decl_spec.policy_cls,
            )
            condition_cls = (
                self.stage_registry.get_class(policy_decl_spec.condition_cls)
                if policy_decl_spec.condition_cls
                else None
            )
            condition_kwargs = policy_decl_spec.condition_kwargs or {}
            next_stage_ids = policy_decl_spec.next_stage_ids or []

            _condition = (
                condition_cls(condition_kwargs) if condition_cls else None
            )

            policy = PolicySpec(
                id=policy_decl_spec.id,
                policy_cls=policy_cls,
                condition=_condition,
                next_stage_ids=next_stage_ids,
            )
            runtime_policies.register(policy_id, policy)

        return runtime_policies

    # --------------------------
    # Stage building
    # --------------------------
    def build_stage_specs(
        self,
        stages_decl: Buffer[StageDeclSpec],
    ) -> Buffer[StageSpec]:
        runtime_stages: Buffer[StageSpec] = Buffer[StageSpec]()

        for stage_decl_spec in stages_decl.values():
            stage_cls = self.stage_registry.get_class(
                stage_decl_spec.stage_cls,
            )

            if not stage_cls:
                continue

            policy_id = (
                stage_decl_spec.policy_id
                if stage_decl_spec.policy_id
                else None
            )

            stage_spec = StageSpec(
                id=stage_decl_spec.id,
                stage_cls=stage_cls,
                kwargs=stage_decl_spec.kwargs or {},
                policy_id=policy_id,
                before=stage_decl_spec.before_ids or [],
                after=stage_decl_spec.after_ids or [],
            )
            runtime_stages.register(stage_decl_spec.id, stage_spec)

        return runtime_stages

    # --------------------------
    # Public API
    # --------------------------
    def build_pipeline(
        self,
        pipeline_decl: "DeclarativePipeline",
    ) -> list[StageSpec]:
        """Pipeline builder.

        Build a runtime pipeline:
        - First build policies
        - Then build stages and bind policies.
        """
        runtime_policies = self.build_policy_specs(
            pipeline_decl.policy_decl_specs,
        )
        runtime_stages = self.build_stage_specs(
            pipeline_decl.stage_decl_specs, runtime_policies,
        )
        return runtime_stages, runtime_policies

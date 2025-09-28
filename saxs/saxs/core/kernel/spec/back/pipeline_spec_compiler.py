from typing import Dict, List

from saxs.saxs.core.kernel.spec.back.buffer import Buffer
from saxs.saxs.core.kernel.spec.back.runtime_spec import PolicySpec, StageSpec

from saxs.saxs.core.kernel.spec.core.registry import (
    PolicyRegistry,
    StageRegistry,
)
from saxs.saxs.core.kernel.spec.front.declarative_specs import (
    PolicyDeclSpec,
    StageDeclSpec,
)
from saxs.saxs.core.kernel.spec.front.parser import DeclarativePipeline
from saxs.saxs.core.stage.abstract_cond_stage import (
    AbstractRequestingStage,
    AbstractStage,
)
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class PipelineSpecCompiler:
    """
    Builds runtime StageSpec and PolicySpec objects from purely declarative specs.
    - Resolves string references to classes using StageRegistry and PolicyRegistry.
    - Keeps policy and stage building logically separated but in one class.
    """

    def __init__(
        self, stage_registry: "StageRegistry", policy_registry: "PolicyRegistry"
    ):
        self.stage_registry = stage_registry
        self.policy_registry = policy_registry

    # --------------------------
    # Policy building
    # --------------------------
    def _build_policies(
        self, policies_decl: Dict[str, "PolicyDeclSpec"]
    ) -> Buffer[PolicySpec]:
        runtime_policies: Buffer[PolicySpec] = Buffer[PolicySpec]()

        for policy_id, p_ref in policies_decl.items():
            policy_cls = self.policy_registry.get_class(p_ref.policy_cls)
            condition_cls = (
                self.stage_registry.get_class(p_ref.condition_cls)
                if p_ref.condition_cls
                else None
            )
            condition_kwargs = p_ref.condition_kwargs or {}
            next_stage_ids = p_ref.next_stage_ids or []

            policy = PolicySpec(
                id=p_ref.id,
                policy_cls=policy_cls,
                condition_cls=condition_cls,
                condition_kwargs=condition_kwargs,
                next_stage_id=next_stage_ids,
            )
            runtime_policies.register(policy_id, policy)

        return runtime_policies

    # --------------------------
    # Stage building
    # --------------------------
    def _build_stages(
        self,
        stages_decl: List["StageDeclSpec"],
        runtime_policies: Buffer[PolicySpec],
    ) -> List[StageSpec]:
        runtime_stages: List[StageSpec] = []

        for stage_decl_spec in stages_decl:
            stage_cls = self.stage_registry.get_class(stage_decl_spec.stage_cls)
            policy = (
                runtime_policies.get(stage_decl_spec.policy_id)
                if stage_decl_spec.policy_id
                else None
            )

            stage_spec = StageSpec(
                id=stage_decl_spec.id,
                stage_cls=stage_cls,
                kwargs=stage_decl_spec.kwargs or {},
                policy=policy,
                before=stage_decl_spec.before_ids or [],
                after=stage_decl_spec.after_ids or [],
            )
            runtime_stages.append(stage_spec)

        return runtime_stages

    # --------------------------
    # Public API
    # --------------------------
    def build_pipeline(
        self, pipeline_decl: "DeclarativePipeline"
    ) -> List[StageSpec]:
        """
        Build a runtime pipeline:
        - First build policies
        - Then build stages and bind policies
        """
        runtime_policies = self._build_policies(pipeline_decl.policies)
        runtime_stages = self._build_stages(
            pipeline_decl.stages, runtime_policies
        )
        return runtime_stages

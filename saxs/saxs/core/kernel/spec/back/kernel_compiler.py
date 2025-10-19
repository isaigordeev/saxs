from typing import TYPE_CHECKING, List

from saxs.saxs.core.kernel.spec.back.pipeline_spec_compiler import (
    PipelineSpecCompiler,
)
from saxs.saxs.core.kernel.spec.back.policy_builder import PolicyBuilder
from saxs.saxs.core.kernel.spec.back.policy_linker import PolicyLinker
from saxs.saxs.core.kernel.spec.back.stage_builder import StageBuilder
from saxs.saxs.core.kernel.spec.back.stage_linker import StageLinker
from saxs.saxs.core.kernel.spec.front.parser import DeclarativePipeline

if TYPE_CHECKING:
    from saxs.saxs.core.kernel.spec.back.buffer import Buffer
    from saxs.saxs.core.kernel.spec.back.runtime_spec import (
        PolicySpec,
        StageSpec,
    )
    from saxs.saxs.core.kernel.spec.front.declarative_specs import (
        PolicyDeclSpec,
        StageDeclSpec,
    )
    from saxs.saxs.core.stage.abstract_stage import AbstractStage
    from saxs.saxs.core.stage.policy.abstr_chaining_policy import (
        ChainingPolicy,
    )


class BaseStageCompiler:
    def __init__(self):
        pass

    def compile(self):
        policy_decl_specs: Buffer[PolicyDeclSpec] = parser.policy_decl_specs
        stage_decl_specs: Buffer[StageDeclSpec] = parser.stage_decl_specs

        compiler = PipelineSpecCompiler()

        policy_specs: Buffer[PolicySpec] = compiler.build_policy_specs(
            policy_decl_specs
        )
        stage_specs: Buffer[StageSpec] = compiler.build_stage_specs(
            stage_decl_specs
        )

        stage_instance: Buffer[AbstractStage] = StageBuilder.build(stage_specs)
        policy_instance: Buffer[ChainingPolicy] = PolicyBuilder.build(
            policy_specs,
        )

        print(stage_instance)
        print(policy_instance)

        linked_policy_instance: Buffer[ChainingPolicy] = PolicyLinker.link(
            policy_specs, stage_instance, policy_instance
        )
        linked_stage_instance: Buffer[ChainingPolicy] = StageLinker.link(
            stage_specs, stage_instance, policy_instance
        )

        return linked_stage_instance


class YamlCompiler(BaseStageCompiler):
    """Yaml compiler."""

    def get_parser(
        self,
        path_to_yaml: str = "kernel.yaml",
    ) -> DeclarativePipeline:
        """Parser."""
        return DeclarativePipeline.from_yaml(path_to_yaml)

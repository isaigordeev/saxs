"""Kernel compiler.

Transforms declarative pipeline specifications into fully
instantiated and linked stage and policy objects.
"""

from saxs.core.kernel.back.buffer import Buffer
from saxs.core.kernel.back.pipeline_spec_compiler import SpecCompiler
from saxs.core.kernel.back.policy_builder import PolicyBuilder
from saxs.core.kernel.back.policy_linker import PolicyLinker
from saxs.core.kernel.back.runtime_spec import PolicySpec, StageSpec
from saxs.core.kernel.back.stage_builder import StageBuilder
from saxs.core.kernel.back.stage_linker import StageLinker
from saxs.core.kernel.front.declarative_specs import (
    PolicyDeclSpec,
    StageDeclSpec,
)
from saxs.core.kernel.front.parser import DeclarativePipeline
from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class BaseCompiler:
    """Base compiler for building and linking pipeline components."""

    def build(
        self,
        stage_specs: Buffer[StageSpec],
        policy_specs: Buffer[PolicySpec],
    ) -> tuple[Buffer[IAbstractStage], Buffer[IAbstractChainingPolicy]]:
        """Build and link stage and policy instances from specs."""
        stage_instance: Buffer[IAbstractStage] = StageBuilder.build(
            stage_specs,
        )
        policy_instance: Buffer[IAbstractChainingPolicy] = PolicyBuilder.build(
            policy_specs,
        )

        PolicyLinker.link(
            policy_specs,
            stage_instance,
            policy_instance,
        )
        linked_stage_instance: Buffer[IAbstractStage] = StageLinker.link(
            stage_specs,
            stage_instance,
            policy_instance,
        )

        return linked_stage_instance, policy_instance


class YamlCompiler(BaseCompiler):
    """Compiler for YAML-based pipeline definitions."""

    @staticmethod
    def get_parser(
        path_to_yaml: str = "kernel.yaml",
    ) -> DeclarativePipeline:
        return DeclarativePipeline.from_yaml(path_to_yaml)

    def compile(self):
        _parser = self.get_parser()
        policy_decl_specs = _parser.policy_decl_specs
        stage_decl_specs = _parser.stage_decl_specs
        return self.build_from_decl(stage_decl_specs, policy_decl_specs)

    def build_from_decl(
        self,
        stage_decl_specs: Buffer[StageDeclSpec],
        policy_decl_specs: Buffer[PolicyDeclSpec],
    ) -> tuple[Buffer[IAbstractStage], Buffer[IAbstractChainingPolicy]]:
        """Compile from declarative specs to linked instances."""
        compiler = SpecCompiler()
        stage_specs = compiler.build_stage_specs(stage_decl_specs)
        policy_specs = compiler.build_policy_specs(policy_decl_specs)
        return self.build(stage_specs, policy_specs)

"""Kernel compiler.

Module for building and linking pipeline stages and policies from
declarative specifications.

This module defines compilers that transform declarative pipeline
specifications (e.g., YAML-based or programmatic) into fully
instantiated and linked stage and policy objects for the SAXS
processing pipeline. The compilation process includes building
stage and policy specifications, instantiating stage and policy
objects, and linking them according to dependencies.

The module provides a base compiler (`BaseCompiler`) for general
compilation logic and a `YamlCompiler` for parsing and compiling
from YAML configuration files.

Classes
-------
BaseCompiler
    Provides the core logic for building stage and policy
    instances from declarative specifications, including linking
    stages and policies.
YamlCompiler
    Extends `BaseCompiler` to parse YAML pipeline specifications
    and compile linked stage and policy objects.

Examples
--------
>>> from saxs.saxs.core.kernel.core.core.compiler import
YamlCompiler
>>> compiler = YamlCompiler()
>>> stages, policies = compiler.compile()
>>> stages
Buffer([...])  # Linked stage instances
>>> policies
Buffer([...])  # Linked policy instances

Notes
-----
- Uses `SpecCompiler` to transform declarative specifications into
internal `PolicySpec` and `StageSpec` buffers.
- `StageBuilder` and `PolicyBuilder` create concrete instances
from specs.
- `StageLinker` and `PolicyLinker` establish dependencies between
stages and policies.
- Designed to integrate seamlessly with YAML-based pipeline
definitions.
"""

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.pipeline_spec_compiler import (
    SpecCompiler,
)
from saxs.saxs.core.kernel.core.back.policy_builder import PolicyBuilder
from saxs.saxs.core.kernel.core.back.policy_linker import PolicyLinker
from saxs.saxs.core.kernel.core.back.runtime_spec import (
    PolicySpec,
    StageSpec,
)
from saxs.saxs.core.kernel.core.back.stage_builder import StageBuilder
from saxs.saxs.core.kernel.core.back.stage_linker import StageLinker
from saxs.saxs.core.kernel.core.front.declarative_specs import (
    PolicyDeclSpec,
    StageDeclSpec,
)
from saxs.saxs.core.kernel.core.front.parser import DeclarativePipeline
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)


class BaseCompiler:
    """Compiler for kernel.

    Base compiler for building and linking pipeline stages and
    policies.

    This class provides the core functionality to transform
    declarative stage and policy specifications into fully
    instantiated and linked objects for the SAXS pipeline.
    """

    def build(
        self,
        stage_specs: Buffer[StageSpec],
        policy_specs: Buffer[PolicySpec],
    ) -> tuple[Buffer[IAbstractStage], Buffer[IAbstractChainingPolicy]]:
        """
        Build and link stage and policy instances.

        This method orchestrates the compilation process:
        1. Converts declarative specifications into internal
          `StageSpec` and `PolicySpec` objects using `SpecCompiler`.
        2. Instantiates concrete stage and policy objects using
           `StageBuilder` and `PolicyBuilder`.
        3. Links the stage and policy objects according to
            dependencies using `StageLinker` and `PolicyLinker`.

        Parameters
        ----------
        policy_decl_specs : Buffer[PolicyDeclSpec]
            Buffer containing declarative policy specifications.
        stage_decl_specs : Buffer[StageDeclSpec]
            Buffer containing declarative stage specifications.

        Returns
        -------
        tuple[Buffer[AbstractStage], Buffer[ChainingPolicy]]
            A tuple containing:
            - Buffer of linked stage instances
            - Buffer of linked policy instances

        Notes
        -----
        - The returned instances are fully linked and ready for
        execution in the SAXS processing pipeline.
        """
        stage_instance: Buffer[IAbstractStage] = StageBuilder.build(
            stage_specs,
        )
        policy_instance: Buffer[IAbstractChainingPolicy] = PolicyBuilder.build(
            policy_specs,
        )

        linked_policy_instance: Buffer[IAbstractChainingPolicy] = (
            PolicyLinker.link(
                policy_specs,
                stage_instance,
                policy_instance,
            )
        )
        linked_stage_instance: Buffer[IAbstractStage] = StageLinker.link(
            stage_specs,
            stage_instance,
            policy_instance,
        )

        return linked_stage_instance, linked_policy_instance


class YamlCompiler(BaseCompiler):
    """Yaml compiler."""

    @staticmethod
    def get_parser(
        path_to_yaml: str = "kernel.yaml",
    ) -> DeclarativePipeline:
        """Parser."""
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
        """
        Build and link stage and policy instances.

        This method orchestrates the compilation process:
        1. Converts declarative specifications into internal
          `StageSpec` and `PolicySpec` objects using `SpecCompiler`.
        2. Calls build main method for Specs

        Parameters
        ----------
        policy_decl_specs : Buffer[PolicyDeclSpec]
            Buffer containing declarative policy specifications.
        stage_decl_specs : Buffer[StageDeclSpec]
            Buffer containing declarative stage specifications.

        Returns
        -------
        tuple[Buffer[AbstractStage], Buffer[ChainingPolicy]]
            A tuple containing:
            - Buffer of linked stage instances
            - Buffer of linked policy instances

        Notes
        -----
        - The returned instances are fully linked and ready for
        execution in the SAXS processing pipeline.
        """
        compiler = SpecCompiler()

        stage_specs: Buffer[StageSpec] = compiler.build_stage_specs(
            stage_decl_specs,
        )
        policy_specs: Buffer[PolicySpec] = compiler.build_policy_specs(
            policy_decl_specs,
        )

        return self.build(stage_specs, policy_specs)

"""
Module for linking policy instances to next-stage classes.

This module defines the `PolicyLinker` class, responsible for
resolving references between `ChainingPolicy` instances and the
`AbstractStage` instances they operate on. Each policy's
`next_stage_cls` attribute is populated with the correct stage
objects.

This allows policies to be applied dynamically in the SAXS
processing pipeline based on previously built stages.
"""

from saxs.saxs.core.kernel.core.back.buffer import Buffer
from saxs.saxs.core.kernel.core.back.runtime_spec import PolicySpec
from saxs.saxs.core.stage.abstract_stage import AbstractStage
from saxs.saxs.core.stage.policy.abstr_chaining_policy import ChainingPolicy


class PolicyLinker:
    """
    Links policies with their next-stage references.

    Provides a static method to link `ChainingPolicy` instances to
    the corresponding `AbstractStage` instances based on
    declarative pipeline specifications.
    """

    @staticmethod
    def link(
        policy_specs: Buffer[PolicySpec],
        stage_instances: Buffer[AbstractStage],
        policy_instances: Buffer[ChainingPolicy],
    ) -> Buffer[ChainingPolicy]:
        """
        Populate `next_stage_cls` for each policy instance.

        Iterates over all `PolicySpec` objects in `policy_specs`
        and resolves the stages listed in `next_stage_ids`. Only
        stages that exist in `stage_instances` are added. Each
        policy's `next_stage_cls` is updated with the resulting
        stage list.

        Parameters
        ----------
        policy_specs : Buffer[PolicySpec]
            Buffer containing policy specifications, including the
            IDs of the next stages each policy should reference.
        stage_instances : Buffer[AbstractStage]
            Buffer of already instantiated stage objects.
        policy_instances : Buffer[ChainingPolicy]
            Buffer of already instantiated policy objects to be
            linked to stages.

        Returns
        -------
        Buffer[ChainingPolicy]
            The buffer of policy instances, now with their
            `next_stage_cls` attributes populated.

        Notes
        -----
        - Policies with no valid next-stage references are skipped.
        - Only stages that exist in `stage_instances` are linked.
        """
        for id_, _policy_spec in policy_specs.items():
            if not _policy_spec.next_stage_ids:
                continue

            # Resolve next stages
            next_stages: list[AbstractStage] = []

            for next_id in _policy_spec.next_stage_ids:
                _stage = stage_instances.get(next_id)
                if _stage:
                    next_stages.append(_stage)

            if not next_stages:
                continue

            policy_instance = policy_instances.get(id_)
            if not policy_instance:
                continue
            policy_instance.next_stage_cls = next_stages

        return policy_instances

"""
Module: AbstractRequestingStage.

This module defines the `AbstractRequestingStage` base class, which
extends `AbstractStage` to support stage approval requests in a
pipeline.

The `AbstractRequestingStage` class provides a framework for
generating requests that can be processed according to
a chaining policy (`ChainingPolicy`).
Subclasses must implement methods to define a default policy and
create specific stage requests (`StageRequest`).

Key Classes:
    - AbstractRequestingStage: Base class for stages capable of
    requesting downstream approval stages.
"""

from abc import abstractmethod
from typing import TypedDict

from saxs.saxs.core.pipeline.scheduler.abstract_stage_request import (
    StageApprovalRequest,
)
from saxs.saxs.core.stage.abstract_stage import (
    IAbstractStage,
    TStageMetadata,
)
from saxs.saxs.core.stage.policy.abstract_chaining_policy import (
    IAbstractChainingPolicy,
)
from saxs.saxs.core.stage.request.abst_request import (
   IAbstractStageRequest,
)
from saxs.saxs.core.types.flow_metadata import FlowMetadata


class EvalSchemaDict(TypedDict, total=False):  # must be generic
    """Abstract eval dictionary schema."""


class IAbstractRequestingStage(
    IAbstractStage[TStageMetadata],
):
    """
    Base class for stages that can generate stage approval requests.

    This class extends `AbstractStage` and provides a mechanism for
    requesting subsequent stages via a chaining policy. Subclasses
    must define a default policy and the logic for creating stage
    requests.

    Attributes
    ----------
        policy (ChainingPolicy | None): The policy used to handle
        stage requests.
    """

    def __init__(
        self,
        metadata: TStageMetadata,
        policy: IAbstractChainingPolicy | None,
    ):
        self.policy = policy
        super().__init__(metadata)

    def request_stage(
        self,
        metadata: FlowMetadata,
    ) -> list[StageApprovalRequest]:
        """
        Generate stage approval requests according to the policy.

        If no policy is set, the default policy provided by
        `default_policy()` will be used. If the policy or generated
        request is empty, an empty list is returned.

        Returns
        -------
            list[StageApprovalRequest]: A list of stage approval
            requests.
        """
        if self.policy is None:  # better policy fallback
            default = self.default_policy()
            self.policy = default

        if not self.policy:  # fallback on policy absence
            return []

        _request = self.create_request(metadata)

        if not _request:  # no request made
            return []

        return self.policy.request(_request)

    def default_policy(
        self,
    ) -> IAbstractChainingPolicy | None:
        """
        Provide the default chaining policy for this stage.

        Subclasses should override this method to supply a fallback
        policy when no explicit policy is set. By default, returns
        a policy that does not inject any requests.

        Returns
        -------
            ChainingPolicy: The default chaining policy.
        """

    @abstractmethod
    def create_request(
        self,
        metadata: FlowMetadata,
    ) -> IAbstractStageRequest:
        """
        Create a stage request for the current stage.

        Subclasses must implement this method to define the logic
        for generating a `StageRequest` object, which will later be
        passed to the chaining policy.

        Returns
        -------
            StageRequest: The generated stage request.
        """

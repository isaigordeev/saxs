"""abstr_chaining_policy module.

Defines the abstract base class for stage chaining policies in SAXS pipelines.

This module provides the foundation for implementing different strategies
for chaining stages together based on conditions and metadata. Chaining
policies determine which stages should be injected into the pipeline after
a given stage completes its processing.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypedDict

from saxs.core.stage.abstract_stage import IAbstractStage
from saxs.core.stage.request.abst_request import (
    StageRequest,
)

if TYPE_CHECKING:
    from saxs.core.pipeline.condition.abstract_condition import (
        StageCondition,
    )
    from saxs.core.pipeline.scheduler.abstract_stage_request import (
        StageApprovalRequest,
    )


class EvalSchemaDict(TypedDict, total=False):
    """Abstract evaluation dictionary schema.

    TypedDict schema for evaluation metadata used in stage condition
    evaluation. This serves as a base schema that can be extended by
    concrete implementations to define specific metadata fields.
    """


class IAbstractChainingPolicy(ABC):
    """Abstract base class for stage chaining policies.

    A chaining policy determines how stages are connected in a pipeline
    by evaluating conditions and deciding which stages should be injected
    next. This class provides the interface that all concrete chaining
    policies must implement.

    Attributes
    ----------
    condition : StageCondition
        Condition evaluated to determine whether to inject pending stages.
    pending_stages : list[IAbstractStage[Any]]
        List of stages that may be injected based on condition evaluation.
    """

    def __init__(
        self,
        condition: "StageCondition",
        pending_stages: list[IAbstractStage[Any]],
    ):
        """Initialize the chaining policy.

        Parameters
        ----------
        condition : StageCondition
            Condition used to evaluate whether to inject pending stages.
        pending_stages : list[IAbstractStage[Any]]
            List of stages that may be injected into the pipeline.
        """
        self.condition = condition
        self.pending_stages: list[IAbstractStage[Any]] = pending_stages

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest,
    ) -> list["StageApprovalRequest"]:
        """Evaluate condition and request stage injection.

        Evaluates the policy's condition against the provided request
        metadata and determines which stages should be injected into
        the pipeline based on the evaluation result.

        Parameters
        ----------
        request_metadata : StageRequest
            Metadata from the current stage containing evaluation data,
            flow metadata, and scheduler information.

        Returns
        -------
        list[StageApprovalRequest]
            List of stage approval requests for stages to be injected.
            Empty list if condition fails or no stages should be injected.
        """

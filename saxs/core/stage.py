"""Abstract base classes for pipeline stages, policies, and requests."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from saxs.logging.logger import get_logger

from saxs.core.types import FlowMetadata, SAXSSample

if TYPE_CHECKING:
    pass

logger = get_logger(__name__, "policy")


# ---------------------------------------------------------------------------
# Stage approval request
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StageApprovalRequest:
    """Request for a stage to be approved and added to the pipeline."""

    stage: "IAbstractStage"


# ---------------------------------------------------------------------------
# Stage request
# ---------------------------------------------------------------------------


@dataclass
class IAbstractStageRequest:
    """Base class for stage addition requests."""


@dataclass
class StageRequest(IAbstractStageRequest):
    """Request for adding a new stage to the pipeline.

    Attributes
    ----------
    condition_eval_metadata : FlowMetadata
        Metadata used to evaluate the chaining condition.
    flow_metadata : FlowMetadata
        Metadata passed to the next stage.
    """

    condition_eval_metadata: FlowMetadata
    flow_metadata: FlowMetadata


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------


class SampleCondition(ABC):
    """Condition evaluated against sample metadata."""

    @abstractmethod
    def evaluate(self, eval_metadata: "SampleMetadata") -> bool:
        """Return True if the condition passes."""


class StageCondition(ABC):
    """Condition evaluated against flow metadata for stage chaining."""

    @abstractmethod
    def evaluate(self, eval_metadata: FlowMetadata) -> bool:
        """Return True if the condition passes."""


# ---------------------------------------------------------------------------
# Chaining policy
# ---------------------------------------------------------------------------


class IAbstractChainingPolicy(ABC):
    """Determines which stages to inject after a stage completes."""

    def __init__(
        self,
        condition: StageCondition,
        pending_stages: list["IAbstractStage"],
    ):
        self.condition = condition
        self.pending_stages: list["IAbstractStage"] = pending_stages

    @abstractmethod
    def request(
        self,
        request_metadata: StageRequest,
    ) -> list[StageApprovalRequest]:
        """Evaluate condition and return approval requests."""


class SingleStageChainingPolicy(IAbstractChainingPolicy):
    """Policy that injects at most one next stage based on a condition."""

    def __init__(
        self,
        condition: StageCondition,
        pending_stages: list["IAbstractStage"],
    ):
        if len(pending_stages) > 1:
            msg = (
                f"{self.__class__.__name__} expects at most one next stage, "
                f"got {len(pending_stages)}"
            )
            raise ValueError(msg)
        super().__init__(condition, pending_stages)

    def request(
        self,
        request_metadata: StageRequest,
    ) -> list[StageApprovalRequest]:
        """Evaluate condition and return a stage request if it passes."""
        if not self.condition:
            logger.info("No condition set, skipping injection")
            return []

        _eval_metadata = request_metadata.condition_eval_metadata

        if self.condition.evaluate(eval_metadata=_eval_metadata):
            _pending_stage: IAbstractStage = self.pending_stages[0]

            logger.stage_info(
                _pending_stage.__class__.__name__,
                "Injecting stage",
                condition=self.condition.__class__.__name__,
            )

            return [
                StageApprovalRequest(stage=_pending_stage),
            ]

        logger.info("Condition failed | No stage injected")
        return []


# ---------------------------------------------------------------------------
# Abstract stage
# ---------------------------------------------------------------------------


class IAbstractStage(ABC):
    """Base class for a processing stage in a SAXS data pipeline."""

    def __init__(self, metadata: Any = None):
        self.metadata = metadata

    def process(
        self,
        sample: SAXSSample,
        flow_metadata: FlowMetadata,
    ) -> tuple[SAXSSample, FlowMetadata]:
        """Process sample data with metadata hooks."""
        _sample = self._prehandle_flow_metadata(sample, flow_metadata)
        _sample = self._process(_sample)
        _flow_metadata = self._posthandle_flow_metadata(_sample, flow_metadata)
        return _sample, _flow_metadata

    @abstractmethod
    def _process(self, sample: SAXSSample) -> SAXSSample:
        """Implement stage-specific processing logic."""
        raise NotImplementedError

    def _posthandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> FlowMetadata:
        """Hook for updating flow metadata after processing."""
        _ = _sample
        return _flow_metadata

    def _prehandle_flow_metadata(
        self,
        _sample: SAXSSample,
        _flow_metadata: FlowMetadata,
    ) -> SAXSSample:
        """Hook for updating sample from flow metadata before processing."""
        _ = _flow_metadata
        return _sample

    def request_stage(
        self,
        metadata: FlowMetadata,
    ) -> list[StageApprovalRequest]:
        """Optionally request additional stages based on flow metadata."""
        _ = metadata
        return []


# ---------------------------------------------------------------------------
# Requesting stage (can chain to other stages)
# ---------------------------------------------------------------------------


class IAbstractRequestingStage(IAbstractStage):
    """Stage that can request injection of other stages via a policy."""

    def __init__(
        self,
        metadata: Any = None,
        policy: IAbstractChainingPolicy | None = None,
    ):
        self.policy = policy
        super().__init__(metadata)

    def request_stage(
        self,
        metadata: FlowMetadata,
    ) -> list[StageApprovalRequest]:
        """Generate stage approval requests via the chaining policy."""
        if self.policy is None:
            default = self.default_policy()
            self.policy = default

        if not self.policy:
            return []

        _request = self.create_request(metadata)

        if not _request:
            return []

        return self.policy.request(_request)

    def default_policy(self) -> IAbstractChainingPolicy | None:
        """Provide a fallback policy. Override in subclasses."""
        return None

    @abstractmethod
    def create_request(
        self,
        metadata: FlowMetadata,
    ) -> IAbstractStageRequest:
        """Create a stage request based on current flow metadata."""


# Re-import SampleMetadata for the forward reference
from saxs.core.types import SampleMetadata  # noqa: E402

__all__ = [
    "IAbstractChainingPolicy",
    "IAbstractRequestingStage",
    "IAbstractStage",
    "IAbstractStageRequest",
    "SampleCondition",
    "SingleStageChainingPolicy",
    "StageApprovalRequest",
    "StageCondition",
    "StageRequest",
]

"""Scheduler metadata types."""

from dataclasses import dataclass, field


@dataclass
class SchedulerMetadata:
    """Metadata for scheduler operations."""

    processed_count: int = 0
    peaks: set[int] = field(default_factory=set)

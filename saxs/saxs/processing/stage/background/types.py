from dataclasses import field
from typing import Any, Callable

import numpy as np

from saxs.saxs.core.types.metadata import (
    AbstractMetadata,
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)


class EBackMetadataKeys(EMetadataSchemaKeys):
    """Enum of keys used in BackgroundStageMetadataDict."""

    BACKGROUND_FUNC = "background_func"
    BACKGROUND_COEF = "background_coef"


class BackgroundStageMetadataDict(MetadataSchemaDict, total=False):
    """
    Schema for Cut stage metadata.

    Attributes
    ----------
    cut_point : int
        Index or position representing the cut point
        in the SAXS data array.
    """

    background_func: Callable[..., NDArray[np.float64]]
    background_coef: float


class BackgroundStageMetadata(AbstractMetadata[BackgroundStageMetadataDict]):
    """
    Metadata object representing the Cut stage configuration.

    Provides a builder-style, type-safe interface around
    a `CutStageMetadataDict` dictionary, with convenient
    accessors and default initialization.

    Attributes
    ----------
    value : CutStageMetadataDict
        Underlying metadata dictionary, defaulting to
        `{"cut_point": 0}`.
    """

    value: BackgroundStageMetadataDict = field(
        default_factory=lambda: {
            EBackMetadataKeys.BACKGROUND_COEF.value: 0.3,
        },
    )

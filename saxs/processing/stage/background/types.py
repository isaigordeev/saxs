from collections.abc import Callable
from dataclasses import field

import numpy as np
from numpy.typing import NDArray

from saxs.saxs.core.types.metadata import (
    EMetadataSchemaKeys,
    MetadataSchemaDict,
)
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata

# Background subtraction coefficient
# NOTE: Value of 0.7 (not 1.0) is empirically determined to prevent
# over-subtraction that would create negative intensities.
# See TECHNICAL_INSIGHTS_LEGACY_PEAK.md section 1.3 for details.
BACKGROUND_COEF = 0.7


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


class BackgroundStageMetadata(
    TAbstractStageMetadata[BackgroundStageMetadataDict, EBackMetadataKeys],
):
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

    Keys = EBackMetadataKeys
    Dict = BackgroundStageMetadataDict

    value: BackgroundStageMetadataDict = field(
        default_factory=lambda: {
            EBackMetadataKeys.BACKGROUND_COEF.value: 0.3,
        },
    )

"""
Module: sample_data_wrappers.

This module defines typed, immutable data wrappers used in SAXS
(Small-Angle X-ray Scattering) pipelines. These wrappers encapsulate
array-like data and
metadata in strongly typed structures that inherit from
`BaseDataType`.

Each class provides semantic meaning for the type of scientific data
it holds, enabling safer and clearer handling of SAXS data objects
throughout the processing pipeline.

Classes:
    - QValues: Represents the scattering vector magnitudes
        (q-values).
    - Intensity: Represents measured scattering intensity values.
    - IntensityError: Represents uncertainties associated with
        intensity data.
    - AbstractSampleMetadata: Represents structured sample metadata.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from saxs.saxs.core.types.abstract_data import TBaseDataType


@dataclass(frozen=False)
class QValues(TBaseDataType[NDArray[np.float64]]):
    """
    Represents the scattering vector magnitudes (q-values).

    Attributes
    ----------
        values (NDArray[np.float64]): 1D or ND array of q-values
        (in Å⁻¹).
    """


@dataclass(frozen=False)
class Intensity(TBaseDataType[NDArray[np.float64]]):
    """
    Represents the measured SAXS intensity data.

    Attributes
    ----------
        values (NDArray[np.float64]): 1D or ND array of intensity
        values.
    """


@dataclass(frozen=False)
class IntensityError(TBaseDataType[NDArray[np.float64]]):
    """
    Represents the measurement errors of intensity data.

    Attributes
    ----------
        values (Optional[NDArray[np.float64]]): 1D or ND array of
        intensity uncertainties. Can be None if errors are
        unavailable.
    """


@dataclass(frozen=False)
class AbstractSampleMetadata(TBaseDataType[dict[str, Any]]):
    """
    Represents metadata associated with a SAXS sample.

    Attributes
    ----------
        values (dict[str, Any]): Dictionary containing metadata
        entries such as sample name, concentration, temperature, or
        comments.
    """

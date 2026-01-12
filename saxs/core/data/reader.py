"""
Module: saxs.io.data_reader.

Data reading utilities for the SAXS project.

This module provides the `DataReader` class, which supports reading
numerical scattering data from CSV files and constructing
`SAXSSample` objects from the loaded arrays.

The expected CSV structure is either:
- Two columns: q-values, intensity
- Three columns: q-values, intensity, intensity error

Examples
--------
>>> reader = DataReader("example_data.csv")
>>> q, i, di = reader.read_data()
>>> sample = reader.create_sample(q, i, di)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from saxs.core.types.sample import (
    ESAXSSampleKeys,
    SAXSSample,
    SAXSSampleDict,
)
from saxs.core.types.sample_objects import (
    Intensity,
    IntensityError,
    QValues,
    SampleMetadata,
)

if TYPE_CHECKING:
    from numpy.typing import NDArray


class DataReader:
    """Read and process numeric data from CSV files."""

    def __init__(self, file_path: str | Path) -> None:
        """Initialize with the path to a data file."""
        self.file_path: Path = Path(file_path)
        self.data: pd.DataFrame | None = None

    def read_data(
        self,
    ):
        """
        Read numeric SAXS data from a CSV file.

        The CSV file is expected to have at least two numeric
        columns:
        - First column: q-values.
        - Second column: intensities.
        - Third column (optional): intensity errors.

        Non-numeric entries are automatically coerced to NaN and
        removed from the dataset.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray | None]
            A tuple containing:
            - q : q-values array.
            - i : intensity array.
            - di : intensity-error array, or None if absent.

        Raises
        ------
        ValueError
            If the file extension is not `.csv` or contains
            fewer than two numeric columns.
        """
        extension: str = self.file_path.suffix.lower()
        if extension != ".csv":
            msg = f"Unsupported file type: {extension}."
            "Only CSV files are supported."
            raise ValueError(msg)

        # Read CSV and coerce non-numeric values to NaN
        data = pd.read_csv(self.file_path, sep=",")
        data = data.apply(pd.to_numeric, errors="coerce").dropna()
        self.data = data

        # Extract columns
        num_cols = data.shape[1]
        if num_cols >= 3:
            q = np.asarray(data.iloc[:, 0])
            i = np.asarray(data.iloc[:, 1])
            di = np.asarray(data.iloc[:, 2])
            return q, i, di

        if num_cols == 2:
            q = np.asarray(data.iloc[:, 0])
            i = np.asarray(data.iloc[:, 1])
            return q, i, None

        msg = "CSV file must contain at least two columns."
        raise ValueError(msg)

    def create_sample(
        self,
        q: NDArray[np.float64],
        i: NDArray[np.float64],
        di: NDArray[np.float64],
    ):
        """
        Construct a `SAXSSample` object from raw q, i, and di.

        Parameters
        ----------
        q : NDArray[np.float64]
            Array of q-values.
        i : NDArray[np.float64]
            Array of intensities.
        di : NDArray[np.float64] | None
            Array of intensity errors, or None if unavailable.

        Returns
        -------
        SAXSSample
            A fully constructed SAXSSample instance ready for
            processing.
        """
        _q = QValues(q)
        _i = Intensity(i)
        _di = IntensityError(di)

        _value = SAXSSampleDict(
            {
                ESAXSSampleKeys.Q_VALUES.value: _q,
                ESAXSSampleKeys.INTENSITY.value: _i,
                ESAXSSampleKeys.INTENSITY_ERROR.value: _di,
                ESAXSSampleKeys.METADATA.value: SampleMetadata(
                    {},
                ),  # optional if metadata needed
            },
        )

        return SAXSSample(_value)

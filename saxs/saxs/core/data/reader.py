"""Data reading utilities for SAXS project."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.sample_objects import (
    Intensity,
    IntensityError,
    QValues,
)


class DataReader:
    """Read and process numeric data from CSV files."""

    def __init__(self, file_path: str | Path) -> None:
        """Initialize with the path to a data file."""
        self.file_path: Path = Path(file_path)
        self.data: pd.DataFrame | None = None

    def read_data(
        self,
    ):
        """Read sample.

        Read data from the file path and return columns
        as NumPy arrays.
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

    def create_sample(self, q, i, di):
        _q = QValues(q)
        _i = Intensity(i)
        _di = IntensityError(di)
        return SAXSSample(q_values=_q, intensity=_i, intensity_error=_di)

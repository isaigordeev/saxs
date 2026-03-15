"""Data reading utilities for SAXS.

Reads CSV files and constructs SAXSSample objects.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from saxs.core.types import SAXSSample, SampleMetadata

if TYPE_CHECKING:
    from numpy.typing import NDArray


class DataReader:
    """Read and process numeric data from CSV files."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path: Path = Path(file_path)
        self.data: pd.DataFrame | None = None

    def read_data(self):
        """Read numeric SAXS data from a CSV file.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray | None]
            q-values, intensities, and optional intensity errors.
        """
        extension: str = self.file_path.suffix.lower()
        if extension != ".csv":
            msg = f"Unsupported file type: {extension}. Only CSV files are supported."
            raise ValueError(msg)

        data = pd.read_csv(self.file_path, sep=",")
        data = data.apply(pd.to_numeric, errors="coerce").dropna()
        self.data = data

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
    ) -> SAXSSample:
        """Construct a SAXSSample from raw arrays."""
        return SAXSSample(
            q_values=q,
            intensity=i,
            intensity_err=di,
            metadata=SampleMetadata(),
        )

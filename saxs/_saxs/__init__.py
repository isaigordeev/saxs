"""Python bindings for Rust SAXS functions."""

import ctypes
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

_LIB_PATH = Path(__file__).parent / "target" / "release" / "lib_saxs.dylib"
_lib = ctypes.CDLL(str(_LIB_PATH))

# find_max(data, len, out_index) -> max_value
_lib.find_max.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
_lib.find_max.restype = ctypes.c_double


def find_max(data: NDArray[np.float64]) -> tuple[float, int]:
    """Find maximum value and its index in array.

    Parameters
    ----------
    data : NDArray[np.float64]
        Input array of float64 values.

    Returns
    -------
    tuple[float, int]
        (max_value, index)

    """
    arr = np.ascontiguousarray(data, dtype=np.float64)
    index = ctypes.c_size_t()

    max_val = _lib.find_max(
        arr.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        len(arr),
        ctypes.byref(index),
    )

    return float(max_val), int(index.value)

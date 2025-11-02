"""Simple funcs.

Simple functions.
"""  # noqa: EXE002

import numpy as np
from numpy.typing import NDArray


def background_exponent(
    x: NDArray[np.float64],
    a: float,
    b: float,
) -> NDArray[np.float64]:
    """
    Calculate an exponential background function.

    Parameters
    ----------
    x : np.ndarray
        input array
    a : float
        exponential coefficient
    b : float
        amplitude

    Returns
    -------
    np.ndarray
        background values for each x
    """
    return b * np.exp(x * a)


def background_hyperbole(
    x: NDArray[np.float64],
    a: float,
    b: float,
) -> NDArray[np.float64]:
    """
    Calculate a hyperbolic background function.

    Parameters
    ----------
    x : np.ndarray
        input array
    a : float
        power exponent
    b : float
        amplitude

    Returns
    -------
    np.ndarray
        background values for each x
    """
    return b * x ** (-a)


def gauss(
    x: NDArray[np.float64],
    mu: float,
    sigma: float,
    ampl: float,
) -> NDArray[np.float64]:
    """
    Calculate a gaussian function.

    Parameters
    ----------
    x : np.ndarray
        input array
    mu : float
        mean of the gaussian
    sigma : float
        standard deviation
    ampl : float
        amplitude

    Returns
    -------
    np.ndarray
        gaussian values for each x
    """
    return ampl * np.exp(-((x - mu) ** 2) / (sigma**2))


def parabole(
    x: NDArray[np.float64],
    mu: float,
    sigma: float,
    ampl: float,
) -> NDArray[np.float64]:
    """
    Calculate a parabolic function.

    Parameters
    ----------
    x : np.ndarray
        input array
    mu : float
        center of the parabola
    sigma : float
        width parameter
    ampl : float
        amplitude

    Returns
    -------
    np.ndarray
        parabolic values for each x
    """
    return ampl * (1 - (x - mu) ** 2 / (sigma**2))


def gaussian_sum(
    x: NDArray[np.float64],
    *params: float,
) -> NDArray[np.float64]:
    """
    Sum of multiple gaussian functions.

    Parameters
    ----------
    x : np.ndarray
        input array
    *params : float
        sequence of gaussian parameters in groups of three
        (mean, amplitude, standard deviation)

    Returns
    -------
    np.ndarray
        summed gaussian values for each x
    """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        mean, amplitude, std_dev = params[i : i + 3]
        y += amplitude * np.exp(-(((x - mean) / std_dev) ** 2))
    return y


def moving_average(
    data: NDArray[np.float64],
    window_size: int,
) -> NDArray[np.float64]:
    """
    Compute moving average of a 1D array.

    Parameters
    ----------
    data : np.ndarray
        input data array
    window_size : int
        size of the moving window

    Returns
    -------
    np.ndarray
        smoothed array of same length as data
    """
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode="same")  # pyright: ignore[reportReturnType]

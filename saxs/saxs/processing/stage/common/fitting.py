"""
Module: fitting.

The module relies on `scipy.optimize.curve_fit` for fitting and
supports logging of intermediate and final processing states.
"""

from collections.abc import Callable
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import (  # pyright: ignore[reportMissingTypeStubs]
    curve_fit,  # pyright: ignore[reportUnknownVariableType]
)


class Fitting:
    """Fit methods class from scipy."""

    @staticmethod
    def curve_fit(
        _func: Callable[..., NDArray[np.float64]],
        x_data: NDArray[np.float64],
        y_data: NDArray[np.float64],
        error: NDArray[np.float64],
        p0: tuple[float, ...] | None,
        bounds: tuple[list[Any], ...] | tuple[Any, ...] = (-np.inf, np.inf),
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Fit the background function to intensity data.

        Created for typing scipy function.

        Parameters
        ----------
        _background_func : Callable[..., NDArray[np.float64]]
            The background function to fit.
        q_values : NDArray[np.float64]
            Array of scattering vector values.
        intensity : NDArray[np.float64]
            Array of measured intensities.
        error : NDArray[np.float64]
            Array of intensity measurement errors.

        Returns
        -------
        tuple[NDArray[np.float64], NDArray[np.float64]]
            popt : Optimal parameters for the background function.
            pcov : Covariance of the fitted parameters.
        """
        res_: tuple[NDArray[np.float64], NDArray[np.float64]] = curve_fit(  # pyright: ignore[reportUnknownVariableType]
            f=_func,
            xdata=x_data,
            ydata=y_data,
            p0=p0,
            bounds=bounds,
            sigma=error,
        )

        popt, _pcov = res_  # pyright: ignore[reportUnknownVariableType]

        return popt, _pcov  # pyright: ignore[reportUnknownVariableType]

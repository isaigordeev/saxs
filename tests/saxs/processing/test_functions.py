#
# Created by Isai GORDEEV on 20/09/2025.
#

"""
Tests for functions.py module.
"""

import time
from unittest.mock import patch

import numpy as np
import pytest

from saxs.saxs.processing.functions import (
    background_exponent,
    background_hyberbole,
    gauss,
    gaussian_sum,
    moving_average,
    parabole,
    timer_decorator,
)


class TestBackgroundFunctions:
    """Test cases for background fitting functions."""

    def test_background_exponent_basic(self):
        """Test background_exponent function with basic inputs."""
        x = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        a, b = 2.0, 1.5

        result = background_exponent(x, a, b)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)
        assert np.all(result > 0)  # Should be positive for positive inputs

        # Test with different parameters
        result2 = background_exponent(x, -1.0, 0.5)
        assert isinstance(result2, np.ndarray)
        assert len(result2) == len(x)

    def test_background_exponent_edge_cases(self):
        """Test background_exponent with edge cases."""
        # Test with single value
        x = np.array([1.0])
        result = background_exponent(x, 1.0, 1.0)
        assert result[0] == np.exp(1.0)

        # Test with zero
        x = np.array([0.0])
        result = background_exponent(x, 1.0, 1.0)
        assert result[0] == 1.0

        # Test with negative values
        x = np.array([-1.0, 0.0, 1.0])
        result = background_exponent(x, 1.0, 1.0)
        expected = np.array([np.exp(-1.0), 1.0, np.exp(1.0)])
        np.testing.assert_array_almost_equal(result, expected)

    def test_background_hyberbole_basic(self):
        """Test background_hyberbole function with basic inputs."""
        x = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        a, b = 2.0, 1.5

        result = background_hyberbole(x, a, b)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)
        assert np.all(result > 0)  # Should be positive for positive inputs

        # Test with different parameters
        result2 = background_hyberbole(x, 1.0, 2.0)
        assert isinstance(result2, np.ndarray)
        assert len(result2) == len(x)

    def test_background_hyberbole_edge_cases(self):
        """Test background_hyberbole with edge cases."""
        # Test with single value
        x = np.array([1.0])
        result = background_hyberbole(x, 1.0, 1.0)
        assert result[0] == 1.0

        # Test with different exponents
        x = np.array([0.5, 1.0, 2.0])
        result = background_hyberbole(x, 2.0, 1.0)
        expected = np.array([4.0, 1.0, 0.25])
        np.testing.assert_array_almost_equal(result, expected)

    def test_background_hyberbole_zero_handling(self):
        """Test background_hyberbole with zero and negative values."""
        # Test with zero (should cause division by zero)
        x = np.array([0.0, 0.1, 0.2])
        with pytest.warns(RuntimeWarning):
            background_hyberbole(x, 1.0, 1.0)

        # Test with negative values
        x = np.array([-0.1, 0.1, 0.2])
        result = background_hyberbole(x, 1.0, 1.0)
        assert isinstance(result, np.ndarray)


class TestGaussianFunctions:
    """Test cases for Gaussian-related functions."""

    def test_gauss_basic(self):
        """Test gauss function with basic inputs."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        mu, sigma, ampl = 2.0, 1.0, 1.0

        result = gauss(x, mu, sigma, ampl)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)
        assert np.all(result >= 0)  # Should be non-negative

        # Peak should be at mu
        peak_idx = np.argmax(result)
        assert abs(x[peak_idx] - mu) < 0.1  # Should be close to mu

    def test_gauss_parameters(self):
        """Test gauss function with different parameters."""
        x = np.linspace(-5, 5, 100)

        # Test with different means
        result1 = gauss(x, 0.0, 1.0, 1.0)
        result2 = gauss(x, 2.0, 1.0, 1.0)

        assert isinstance(result1, np.ndarray)
        assert isinstance(result2, np.ndarray)
        assert len(result1) == len(x)
        assert len(result2) == len(x)

        # Test with different amplitudes
        result3 = gauss(x, 0.0, 1.0, 2.0)
        assert np.max(result3) > np.max(
            result1
        )  # Higher amplitude should give higher peak

    def test_gauss_edge_cases(self):
        """Test gauss function with edge cases."""
        x = np.array([0.0])
        mu, sigma, ampl = 0.0, 1.0, 1.0

        result = gauss(x, mu, sigma, ampl)
        assert result[0] == ampl  # At the mean, should equal amplitude

        # Test with very small sigma
        result2 = gauss(x, 0.0, 0.01, 1.0)
        assert result2[0] == ampl

    def test_gaussian_sum_basic(self):
        """Test gaussian_sum function with basic inputs."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        params = [1.0, 1.0, 1.0, 3.0, 0.5, 0.5]  # Two Gaussians

        result = gaussian_sum(x, *params)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)
        assert np.all(result >= 0)  # Should be non-negative

    def test_gaussian_sum_parameter_validation(self):
        """Test gaussian_sum with different parameter counts."""
        x = np.array([0.0, 1.0, 2.0])

        # Test with single Gaussian (3 parameters)
        params1 = [1.0, 1.0, 1.0]
        result1 = gaussian_sum(x, *params1)
        assert isinstance(result1, np.ndarray)

        # Test with two Gaussians (6 parameters)
        params2 = [1.0, 1.0, 1.0, 2.0, 0.5, 0.5]
        result2 = gaussian_sum(x, *params2)
        assert isinstance(result2, np.ndarray)

        # Test with invalid parameter count (should work but may give unexpected results)
        params3 = [1.0, 1.0]  # Only 2 parameters
        with pytest.raises(ValueError):
            result3 = gaussian_sum(x, *params3)

    def test_gaussian_sum_empty_params(self):
        """Test gaussian_sum with empty parameters."""
        x = np.array([0.0, 1.0, 2.0])

        result = gaussian_sum(x)
        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)
        assert np.all(result == 0)  # Should be all zeros


class TestParaboleFunction:
    """Test cases for parabole function."""

    def test_parabole_basic(self):
        """Test parabole function with basic inputs."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        mu, sigma, ampl = 2.0, 1.0, 1.0

        result = parabole(x, mu, sigma, ampl)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(x)

        # Peak should be at mu
        peak_idx = np.argmax(result)
        assert abs(x[peak_idx] - mu) < 0.1  # Should be close to mu

    def test_parabole_parameters(self):
        """Test parabole function with different parameters."""
        x = np.linspace(-2, 2, 100)

        # Test with different means
        result1 = parabole(x, 0.0, 1.0, 1.0)
        result2 = parabole(x, 1.0, 1.0, 1.0)

        assert isinstance(result1, np.ndarray)
        assert isinstance(result2, np.ndarray)
        assert len(result1) == len(x)
        assert len(result2) == len(x)

    def test_parabole_edge_cases(self):
        """Test parabole function with edge cases."""
        x = np.array([0.0])
        mu, sigma, ampl = 0.0, 1.0, 1.0

        result = parabole(x, mu, sigma, ampl)
        assert result[0] == ampl  # At the mean, should equal amplitude

        # Test with very small sigma
        result2 = parabole(x, 0.0, 0.01, 1.0)
        assert result2[0] == ampl


class TestMovingAverageFunction:
    """Test cases for moving_average function."""

    def test_moving_average_basic(self):
        """Test moving_average function with basic inputs."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        window_size = 3

        result = moving_average(data, window_size)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(data)

        # Check that the result is smoothed
        assert np.all(result >= 0)  # Should be non-negative for positive input

    def test_moving_average_window_sizes(self):
        """Test moving_average with different window sizes."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Test with window size 1 (should return original data)
        result1 = moving_average(data, 1)
        np.testing.assert_array_almost_equal(result1, data)

        # Test with window size 2
        result2 = moving_average(data, 2)
        assert isinstance(result2, np.ndarray)
        assert len(result2) == len(data)

        # Test with window size equal to data length
        result3 = moving_average(data, len(data))
        assert isinstance(result3, np.ndarray)
        assert len(result3) == len(data)

    def test_moving_average_edge_cases(self):
        """Test moving_average with edge cases."""
        # Test with single element
        data = np.array([5])
        result = moving_average(data, 1)
        assert result[0] == 5

        # Test with two elements
        data = np.array([1, 2])
        result = moving_average(data, 2)
        assert isinstance(result, np.ndarray)
        assert len(result) == 2

    def test_moving_average_constant_data(self):
        """Test moving_average with constant data."""
        data = np.array([5, 5, 5, 5, 5])
        result = moving_average(data, 3)
        expected = np.array([3.333333, 5.0, 5.0, 5.0, 3.333333])

        # Should return the same constant value
        np.testing.assert_array_almost_equal(result, expected)

    def test_moving_average_negative_values(self):
        """Test moving_average with negative values."""
        data = np.array([-1, -2, -3, -4, -5])
        result = moving_average(data, 3)

        assert isinstance(result, np.ndarray)
        assert len(result) == len(data)
        assert np.all(result <= 0)  # Should be non-positive for negative input


class TestTimerDecorator:
    """Test cases for timer_decorator function."""

    def test_timer_decorator_basic(self):
        """Test timer_decorator with a basic function."""

        @timer_decorator
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

    def test_timer_decorator_with_print(self):
        """Test timer_decorator with print output."""

        @timer_decorator
        def test_func(x):
            time.sleep(0.01)  # Small delay to ensure measurable time
            return x * 2

        with patch("builtins.print") as mock_print:
            result = test_func(5)
            assert result == 10
            mock_print.assert_called_once()
            # Check that the print call contains the function name and execution time
            call_args = mock_print.call_args[0][0]
            assert "test_func" in call_args
            assert "executed in" in call_args

    def test_timer_decorator_preserves_function_metadata(self):
        """Test that timer_decorator preserves function metadata."""

        @timer_decorator
        def test_func(x):
            """Test function docstring."""
            return x * 2

        # Check that the decorator preserves the function's metadata
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."

    def test_timer_decorator_with_args_and_kwargs(self):
        """Test timer_decorator with functions that take args and kwargs."""

        @timer_decorator
        def test_func(x, y=1, z=2):
            return x + y + z

        result = test_func(1, y=3, z=4)
        assert result == 8

    def test_timer_decorator_with_exception(self):
        """Test timer_decorator with functions that raise exceptions."""

        @timer_decorator
        def test_func(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2

        # Test normal case
        result = test_func(5)
        assert result == 10

        # Test exception case
        with pytest.raises(ValueError, match="Negative value"):
            test_func(-1)


class TestFunctionIntegration:
    """Integration tests for processing functions."""

    def test_background_functions_comparison(self):
        """Test that different background functions give different results."""
        x = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        result_exp = background_exponent(x, 1.0, 1.0)
        result_hyp = background_hyberbole(x, 1.0, 1.0)

        # Should give different results
        assert not np.array_equal(result_exp, result_hyp)

        # Both should be positive for positive inputs
        assert np.all(result_exp > 0)
        assert np.all(result_hyp > 0)

    def test_gaussian_functions_consistency(self):
        """Test consistency between gauss and gaussian_sum functions."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])

        # Single Gaussian using gauss
        result1 = gauss(x, 2.0, 1.0, 1.0)

        # Same Gaussian using gaussian_sum
        result2 = gaussian_sum(x, 2.0, 1.0, 1.0)

        np.testing.assert_array_almost_equal(result1, result2)

    def test_smoothing_effect_of_moving_average(self):
        """Test that moving_average actually smooths the data."""
        # Create noisy data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + 0.1 * np.random.randn(100)

        # Apply moving average
        smoothed = moving_average(y, 5)

        # Smoothed data should have less variation
        original_std = np.std(y)
        smoothed_std = np.std(smoothed)

        assert smoothed_std < original_std

    def test_function_parameter_ranges(self):
        """Test functions with various parameter ranges."""
        x = np.linspace(0.1, 5.0, 50)

        # Test background functions with various parameters
        for a in [0.5, 1.0, 2.0]:
            for b in [0.5, 1.0, 2.0]:
                result_exp = background_exponent(x, a, b)
                result_hyp = background_hyberbole(x, a, b)

                assert isinstance(result_exp, np.ndarray)
                assert isinstance(result_hyp, np.ndarray)
                assert len(result_exp) == len(x)
                assert len(result_hyp) == len(x)

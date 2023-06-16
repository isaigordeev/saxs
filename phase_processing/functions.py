import time
from functools import wraps

import numpy as np


def background_exponent(x, a, b):
    return b * np.exp(x * a)


def background_hyberbole(x, a, b):
    return b * x ** (-a)


def gauss(x, c, b):
    return c * np.exp(-(x - 0.04) ** 2 / b)


def parabole(x, mu, sigma, ampl):
    return ampl*(1 - (x - mu) ** 2 / (sigma ** 2))

def gaussian_sum(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        mean, amplitude , std_dev   = params[i:i+3]
        y += amplitude * np.exp(-((x - mean) / std_dev)**2)
    return y

def moving_average(data, window_size):
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode='same')

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} executed in {execution_time} seconds")
        return result
    return wrapper
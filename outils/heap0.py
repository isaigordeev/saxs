import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def gaussian_sum(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        amplitude, mean, std_dev = params[i:i+3]
        y += amplitude * np.exp(-((x - mean) / std_dev)**2)
    return y

# Generate sample data
x = np.linspace(-10, 10, 100)
true_params = [1.0, -2.0, 1.5, 0.5, 0.0, 0.8]  # Amplitude, Mean, Std Dev for 2 Gaussians
y_true = gaussian_sum(x, *true_params)
noise = np.random.normal(0, 0.05, size=len(x))
y = y_true + noise

# Define loss function for optimization
def loss_function(params):
    y_pred = gaussian_sum(x, *params)
    return np.sum((y_pred - y)**2)

# Initial guess for the parameters
initial_guess = [1.0, -1.0, 1.0, 1.0, 0.0, 0.5]

# Perform the fit using gradient descent
result = minimize(loss_function, initial_guess, method='CG')
fitted_params = result.x
y_fit = gaussian_sum(x, *fitted_params)

# Plot the results
plt.plot(x, y, 'b.', label='Data with Noise')
plt.plot(x, y_true, 'g--', label='True Gaussian Sum')
plt.plot(x, y_fit, 'r-', label='Fitted Gaussian Sum')
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.show()

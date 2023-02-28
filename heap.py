import numpy as np
from scipy.signal import savgol_filter

# Generate a noisy signal
t = np.linspace(0, 10, 100)
y = np.sin(t) + np.random.normal(0, 0.1, 100)

# Apply Savitzky-Golay filtering
y_filtered = savgol_filter(y, window_length=5, polyorder=2)

# Plot the original and filtered signals
import matplotlib.pyplot as plt
plt.plot(t, y, label='Original')
plt.plot(t, y_filtered, label='Filtered')
plt.legend()
plt.show()
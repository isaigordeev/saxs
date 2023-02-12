from background_reduction import *
from scipy.signal import find_peaks




difference_filtered = savgol_filter(difference, 15 , 4, deriv=0)
peaks, peaks_data = find_peaks(difference_filtered,
                      height=0,
                      distance = 5,
                      prominence=0.2)
print(q[peaks], peaks, peaks_data)

fig, (ax1, ax2) = plt.subplots(2,1)


ax1.plot(
    # q, I,
    # q, model,
    q, difference,
    # q, difference_filtered,
    q, zeros, label='raw')



ax2.plot(
    q, difference_filtered,
    q[peaks], difference_filtered[peaks],"x",
    label='filtered')


ax1.legend()
ax2.legend()



plt.show()


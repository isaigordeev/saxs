from searching_peaks import *

def peak_function_gauss(x, c, b):
    return c*np.exp(-( x-0.04)**2 / b)

def parabole(x, c, b):
    return c - (x - 0.04) ** 2 / (b**2)


fig, (ax1, ax2) = plt.subplots(2,1)

ax1.plot(
    # q, I,
    # q, model,
    q, difference,
    # q, difference_filtered,
    q, zeros, label='raw')


period1 = 70
period2 = 120

popt, pcov = curve_fit(
    f=parabole,
    xdata=q[period1:period2],
    ydata=difference_filtered[period1:period2],
    # p0 = ( 4, 0.02),
    bounds = (delta_q**2, [2*peaks_data['peak_heights'][0], 1]),
    sigma= dI[period1:period2]
)

print(popt)
# print(parabole(q[period1:period2],0.004, 3.74,  ))


ax2.plot(
    q, difference_filtered,
    q[period1:period2], difference_filtered[period1:period2],
    q[peaks], difference_filtered[peaks],"x",
    q[period1:period2], parabole(q[period1:period2], popt[0], popt[1]),
    q[period1:period2], parabole(q[period1:period2],2, 0.01,  ),
    label='filtered')





ax1.legend()
ax2.legend()

plt.show()
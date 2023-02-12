import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
n_iter = 50
tolerance = 1e-06

df = pd.read_csv("data/095221_xye.csv", sep=';')
# df = pd.read_csv("075773_treated_xye.csv", sep=',')
x = df['Q']
y = df['I']
# print(x)

xe = np.linspace(0, 4, 30)

yhat = savgol_filter(y, 10, 3, deriv=0)
# print(yhat)

# fe = [x**2 for x in xe]
# print(len(fe)-len(xe))
# dfe = [x*2 for x in xe]
# dev = [(fe[i]-fe[i-1])/(xe[i]-xe[i-1]) for i in range(1, len(xe))]

print()
# print(y)
# print(np.gradient(y))
grad = np.gradient(y)
norm_grad = np.gradient(yhat, edge_order=1)
# print(norm_grad)

diff = [grad[i]-grad[i-1] for i in range(len(grad))]
# print(diff)

# norm_diff = [(norm_grad[i]-norm_grad[i-1])/(x[i]-x[i-1]) for i in range(len(norm_grad))]
norm_diff_grad = [(yhat[i]-yhat[i-1])/(x[i]-x[i-1]) for i in range(1,len(norm_grad))]

# print(norm_diff_grad)

# plt.plot( x , y)
# plt.plot(x[200:360] ,yhat[200:360], marker = 'o')
plt.plot(x ,yhat, marker = 'o')

# plt.plot(x, norm_grad)
# x = x[:len(x)-1]
# plt.plot(x[150:], norm_diff_grad[150:])

# plt.plot(xe, fe)
# plt.plot(xe, np.gradient(fe, edge_order=2))
# plt.plot(xe, dfe)
# xe = xe[:len(xe)-1]
# plt.plot(xe, dev)

plt.show()


def gradient_descent(gradient, start, learn_rate):
    vector = start
    for _ in range(n_iter):
        # print(vector, vector**2)
        diff = - learn_rate*gradient(vector)
        if np.all(np.abs(diff) <= tolerance):
            break
        vector += diff

    # return vector


# gradient_descent(gradient= lambda v: 2* v, start = 10, learn_rate=0.2)





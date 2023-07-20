import numpy as np
from saxs.data_generation.data_visualization import plot_saxs

data = np.load('/Users/isaigordeev/Desktop/cache/small_joined_phases.npz')
q = np.load('/Users/isaigordeev/Desktop/cache/cubic_q.npy')

print(*data.keys())
print(data['Im3m'].shape)

print(data['Im3m'].dtype)
print(data['Im3m'][0, :, :, 0].shape)
print(np.sqrt(np.diag(data['Im3m'][0, :, :, 0])).shape)
print(q.shape)

# plot_saxs(q, np.sqrt(np.diag(data['Im3m'][700,:,:,0])))
# plot_saxs(q, np.sqrt(np.diag(data['Im3m'][800,:,:,0])))
# plot_saxs(q, np.sqrt(np.diag(data['Im3m'][900,:,:,0])))

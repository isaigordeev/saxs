import numpy as np

from prominence_kernel import ProminenceKernel


class ParabolePeakKernel(ProminenceKernel):
    def __init__(self, data_dir,
                 is_preprocessing=True,
                 is_background_reduction=True,
                 is_filtering=True,
                 ):
        super().__init__(data_dir,
                         is_preprocessing,
                         is_background_reduction,
                         is_filtering,
                         )

    def negative_reduction(self):
        self.difference = np.maximum(self.current_I_state, 0)



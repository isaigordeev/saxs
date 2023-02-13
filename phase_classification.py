import numpy as np
from fastdtw import fastdtw


class Phase():
    def __init__(self, peaks_q, peaks_I, dI):
        self.la3d = [6, 8, 14, 16, 20, 22, 24, 26]
        self.Pn3m = [2, 3, 4, 6, 8, 9, 10, 11, 12, 14, 16, 17]
        self.Im3m = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
        self.peaks_q = peaks_q
        self.peaks_I = peaks_I
        self.dI = dI
        self.la3d_coeffs = self.ratio_data(0, self.la3d)
        self.Pn3m_coeffs = self.ratio_data(0, self.Pn3m)
        self.Im3m_coeffs = self.ratio_data(0, self.Im3m)

    def ratio_data(self, i, data):
        arr = []
        for x in range(1, len(data) - 1):
            arr = np.append(arr, [np.sqrt(data[x]) / np.sqrt(data[i])])
        return arr

    def score_func(self, f, coeffs):
        distance, path = f(coeffs, self.peaks_q,
                             dist=lambda x, y: abs(x - y))
        return distance, path

    def analyzing(self):
        arr = []
        coeffs = [self.la3d_coeffs, self.Pn3m_coeffs, self.Im3m_coeffs]
        print(coeffs)
        for x in coeffs:
            arr = np.append(arr, self.score_func(fastdtw, x))
        # sorted(arr, key=lambda tuple: tuple[0])
        print(arr, '\n')


peaks_q = [1, 2, 3, 4, 5, 6, 7, 8]
peaks_I = []
dI = []

phase = Phase(peaks_q, peaks_I, dI)
# print(phase.Im3m_coeffs)
phase.analyzing()

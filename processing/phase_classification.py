import numpy as np
from fastdtw import fastdtw

from settings import prominence


class Phase():
    def __init__(self, peaks_q, peaks_I, dI):
        self.la3d = [6, 8, 14, 16, 20, 22, 24, 26]
        self.Pn3m = [2, 3, 4, 6, 8, 9, 10, 11, 12, 14, 16, 17]
        self.Im3m = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]

        self.phases = [[self.la3d],
                       [self.Pn3m],
                       [self.Im3m]]

        self.peaks_q = peaks_q
        self.peaks_I = peaks_I
        self.dI = dI

        self.phases_coeffs = []
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

    def init_phases(self):
        for x in self.phases:
            self.phases_coeffs = np.append(self.phases_coeffs, self.ratio_data(0, x))

    def data_preset(self):
        treshhold = 1.1 * prominence * np.average(self.peaks_I)
        errors = []

        # print(treshhold)
        # print(len(self.peaks_I))

        for x in range(len(self.peaks_I)):
            if self.peaks_I[x] < treshhold:
                errors += [int(x)]
        # print(errors)
        self.peaks_q = np.delete(self.peaks_q, errors)
        self.peaks_I = np.delete(self.peaks_I, errors)

    def analyzing(self):
        arr = []
        coeffs = [self.la3d_coeffs,
                  self.Pn3m_coeffs,
                  self.Im3m_coeffs]
        print(coeffs)
        for x in coeffs:
            arr = np.append(arr, self.score_func(fastdtw, x))
        # sorted(arr, key=lambda tuple: tuple[0])
        return arr

    def alignement(self, arr, i):
        return [self.peaks_q[x] for x, y in arr[i]], [self.phases[i] for x, y in arr[i]]


peaks_q = [0.04377, 0.062262, 0.077603, 0.071582, 0.065066, 0.094616, 0.087276, 0.081695,
           0.10798, 0.11285, 0.13459, 0.1641]
peaks_I = [0.80817437, 6.23131952, 10.85415401, 0.38065323, 0.31464293, 4.16848931,
           2.1762965, 0.75341095, 2.38035013, 0.27138617, 0.45496271, 0.48550016]
dI = []

phase = Phase(peaks_q, peaks_I, dI)
phase.init_phases()
print(phase.phases_coeffs)

# print(phase.Pn3m_coeffs)
# print(phase.Im3m_coeffs)
# print(phase.la3d_coeffs)

print(phase.peaks_q)
print(phase.peaks_I)
phase.data_preset()
print(phase.peaks_q)
print(phase.peaks_I)

print(phase.analyzing())

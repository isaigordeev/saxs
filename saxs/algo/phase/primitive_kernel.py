from saxs.algo.phase.phase_classificator import (
    AbstractPhaseKernel,
)
from saxs.algo.processing_outils import (
    calculate_first_peaks,
)


class PrimitivePhaseKernel(AbstractPhaseKernel):
    def __init__(self, sample, data, phases_dict, phases_coefficients):
        super().__init__(sample, data, phases_dict, phases_coefficients)

    def phase_processing(self):
        self.default_preprocessing_q()
        return self.first_peaks_comparison()

    def first_peaks_comparison(self):
        for i in range(self.phases_number):
            self.distances[i] = calculate_first_peaks(
                self.phases_coefficients[i], self.preprocessed_q
            )

from saxs.gaussian_processing.phase.phase_classificator import AbstractPhaseKernel
from saxs.gaussian_processing.processing_outils import calculate_absolute_difference


class DefaultPhaseKernel(AbstractPhaseKernel):
    def __init__(self, data, sample, phases_dict, phases_coefficients):
        super().__init__(sample, data, phases_dict, phases_coefficients)


    def phase_processing(self):
        self.preprocessing_q()
        self.absolute_sequence_comparison()


    def absolute_sequence_comparison(self):
        for i in range(self.phases_number):
            self.distances[i] = calculate_absolute_difference(self.phases_coefficients[i], self.preprocessed_q)


        # return self.distances
        # print(self.preprocessed_q)
        # print(self.distances)
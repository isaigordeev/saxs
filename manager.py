from peak_classification import *

a = Peaks(q, I, dI)

a.background_reduction()
a.filtering_negative()
# a.peak_searching(height=0., prominence=prominence)
# a.peak_verifying()
# a.plot_diagramme()

a.phase_classification()

print('q', a.peaks_analysed_q)
print('I', a.peaks_analysed_I)
print(sorted(a.peaks_analysed_q) / min(a.peaks_analysed_q))
print('sigma', sorted(a.peaks_analysed_b))

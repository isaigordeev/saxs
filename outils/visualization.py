from processing_outils import read_data, background_plot
from settings_processing import EXTENSION

q, I, _ = read_data('../res/075955_treated_xye', EXTENSION)
background_plot(q[200:], I[200:])

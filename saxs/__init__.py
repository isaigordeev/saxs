import os

from . import data_processing, gaussian_processing, saxs_model

PACKAGE_PATH = os.path.dirname(__file__)
print(PACKAGE_PATH)
DEFAULT_PHASES_PATH = os.path.join(PACKAGE_PATH, 'phases.json')

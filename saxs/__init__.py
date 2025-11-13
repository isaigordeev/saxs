"""SAXS package initialization module.

This module provides package-level constants and initialization
for the SAXS (Small-Angle X-ray Scattering) data processing package.

Constants
---------
PACKAGE_PATH : str
    The absolute path to the package directory.
DEFAULT_PHASES_PATH : str
    The default path to the phases.json configuration file.
"""

import os

PACKAGE_PATH = os.path.dirname(__file__)
DEFAULT_PHASES_PATH = os.path.join(PACKAGE_PATH, "phases.json")

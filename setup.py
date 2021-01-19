# -*- coding: utf-8 -*-
"""
    Setup file for witchcraft.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.3.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys
from pkg_resources import VersionConflict, require
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy as np

try:
    require("setuptools>=38.3")
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

extensions = [
    Extension(
        'witchcraft.bisect_killer.cy_monobound',
        ["src/witchcraft/bisect_killer/cy_monobound.pyx"],
        include_dirs=[np.get_include()], # not needed for fftw unless it is installed in an unusual place
    ),
]

if __name__ == "__main__":
    setup(
        use_pyscaffold=True, 
        py_modules=["sorteddict", "sortedlist"], 
        ext_modules=cythonize(extensions)
    )

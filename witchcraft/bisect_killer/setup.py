# this file is used to compile Cython '*.pyx' source files 
# into modules callable from Python files
# 
# Usage: `python setup.py build_ext --inplace`

from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize(["*.pyx"]),
    include_dirs=[np.get_include()]
)    
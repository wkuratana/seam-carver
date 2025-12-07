# Imports
import numpy
import os
from setuptools import setup, Extension
from Cython.Build import cythonize


extensions = [
    Extension(
        name='seam_carver.wrapper', 
        sources=[
            os.path.join('src', 'seam_carver', 'wrapper.pyx'),
            os.path.join('src', 'seam_carver', 'backend.c'),
            os.path.join('src', 'seam_carver', 'backend2.c')],
        include_dirs=[
            numpy.get_include(), 
            os.path.join('src', 'seam_carver')]
    )
]

setup(
    package_dir={'': 'src'},
    ext_modules=cythonize(extensions)
)
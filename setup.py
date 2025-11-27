# Imports
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy


extensions = [
    Extension(
        name='seam_carver.wrapper', 
        sources=[
            'src/seam_carver/wrapper.pyx'],
        include_dirs=[numpy.get_include()]
    )
]

setup(
    ext_modules=cythonize(extensions)
)
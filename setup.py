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

wrapper = [
    Extension(
        "wrapper",
        ["wrapper.pyx"],
        libraries=[]
    )
]

#TODO: Figure out how to make this non-local

setup(
    ext_modules=cythonize(extensions)
)
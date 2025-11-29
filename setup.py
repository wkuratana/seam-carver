# Imports
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy


# TODO: This is a temp extension for testing the build
extensions = [
    Extension(
        "seam_carver.test_build", 
        sources=["src/seam_carver/backend.c"],
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
from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        ['astar_numpy.py'],
        annotate=True
    )
)

from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        ['astar_numpy_core.py', 'single_source_dijkstra_core.py'],
        annotate=True
    )
)

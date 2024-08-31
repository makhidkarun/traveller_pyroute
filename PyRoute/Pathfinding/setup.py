from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        ['astar_numpy.py', 'single_source_dijkstra_core.py', 'ApproximateShortestPathForestUnified.py',
         'minmaxheap.pyx'],
        annotate=True
    )
)

import os
import sys
import numpy

from setuptools import setup
from Cython.Build import cythonize

sources = [
    "astar_numpy.py",
    "single_source_dijkstra_core.py",
    "ApproximateShortestPathForestUnified.py",
    "minmaxheap.pyx",
    "TradeCalculationRawRoutes.py",
]

compiler_directives={
        "language_level": 3,
        "boundscheck": False,
        "wraparound": False,
        "initializedcheck": False,
        "nonecheck": False,
    }

extensions = cythonize(
    sources,
    annotate=True,
    compiler_directives=compiler_directives
)

if sys.platform == "win32":
    compile_args = ["/O2", "/DNDEBUG"]
else:
    compile_args = ["-O3", "-DNDEBUG"]

    # Enable only for a binary used on the same machine/CPU.
    if os.environ.get("CYTHON_NATIVE") == "1":
        compile_args.append("-march=native")

for extension in extensions:
    extension.include_dirs = list(extension.include_dirs or [])
    extension.include_dirs.append(numpy.get_include())
    extension.extra_compile_args = list(extension.extra_compile_args or [])
    extension.extra_compile_args.extend(compile_args)

setup(
    ext_modules=extensions,
)

"""
Created on Aug 18, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import numpy as np
from _heapq import heappop, heappush, heapify


"""
Created on Nov 30, 2023

@author: CyberiaResurrection

An extension of defaultdict that, as the name says, loudly refuses to accept NoneType keys.
"""
from collections import defaultdict


class NoNoneDefaultDict(defaultdict):

    def __missing__(self, key):
        if key is None:
            raise ValueError("Supplied key must not be NoneType")
        return super().__missing__(key)

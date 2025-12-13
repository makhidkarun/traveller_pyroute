"""
Created on Nov 30, 2023

@author: CyberiaResurrection

An extension of defaultdict that, as the name says, loudly refuses to accept NoneType keys.
"""
from collections import defaultdict


class NoNoneDefaultDict(defaultdict):

    def __init__(self, default_factory=None):
        if default_factory is None:
            raise ValueError("Supplied factory must not be NoneType")
        super(NoNoneDefaultDict, self).__init__(default_factory)

    def __eq__(self, other) -> bool:
        if not isinstance(other, NoNoneDefaultDict):
            return False
        if self.default_factory != other.default_factory:
            return False
        return super().__eq__(other)

    def __hash__(self) -> int:
        return 0

    def __missing__(self, key):
        if key is None:
            raise ValueError("Supplied key must not be NoneType")
        return super().__missing__(key)

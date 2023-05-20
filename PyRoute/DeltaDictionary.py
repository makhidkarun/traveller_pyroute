"""
Created on May 21, 2023

@author: CyberiaResurrection
"""


class DeltaDictionary(dict):

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SectorDictionary), "Values must be SectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SectorDictionary), "Values must be SectorDictionary objects"
        super().__setitem__(item, value)


class SectorDictionary(dict):

    def __init__(self, name, filename):
        super().__init__()
        self.name = name
        self.filename = filename

    def update(self, __m, **kwargs):
        for key in __m:
            assert isinstance(__m[key], SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().update(__m, **kwargs)

    def __setitem__(self, item, value):
        assert isinstance(value, SubsectorDictionary), "Values must be SubsectorDictionary objects"
        super().__setitem__(item, value)


class SubsectorDictionary(dict):

    def __init__(self, name):
        self.name = name
        super().__init__()


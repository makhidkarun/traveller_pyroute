"""
Created on 21 Jul, 2024

@author: CyberiaResurrection
"""
from StatCalculation import ObjectStatistics


class AreaItem(object):
    def __init__(self, name):
        self.name = name
        self.worlds = []
        self.stats = ObjectStatistics()
        self.alg = {}
        self.alg_sorted = []
        self._wiki_name = '[[{}]]'.format(name)
        self.debug_flag = False

    def wiki_title(self) -> str:
        return self.wiki_name()

    def wiki_name(self) -> str:
        return self._wiki_name

    def __str__(self):
        return self.name

    def world_count(self) -> int:
        return len(self.worlds)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def is_well_formed(self) -> tuple[bool, str]:
        return True, ""

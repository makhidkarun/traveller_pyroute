"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
import copy
import contextlib
from typing import Any

from PyRoute.Star import Star
from PyRoute.Utilities.NoNoneDefaultDict import NoNoneDefaultDict
from PyRoute.StatCalculation.Populations import Populations


class ObjectStatistics(object):

    __slots__ = 'population', 'populations', 'economy', 'trade', 'tradeExt', 'tradeVol', 'tradeDton', 'tradeDtonExt',\
                'percapita', 'number', 'milBudget', 'maxTL', 'maxPort', 'maxPop', 'sum_ru', 'shipyards', 'col_be',\
                'im_be', 'passengers', 'spa_people', 'port_size', 'code_counts', 'bases', 'eti_worlds', 'eti_cargo',\
                'eti_pass', 'homeworlds', 'high_pop_worlds', 'high_tech_worlds', 'TLmean', 'TLstddev', 'subsectorCp',\
                'sectorCp', 'otherCp', 'gg_count', 'worlds', 'stars', 'star_count', 'primary_count', '__dict__'

    base_mapping = {'C': 'Corsair base', 'D': 'Naval depot', 'E': 'Embassy', 'K': 'Naval base', 'M': 'Military base',
                    'N': 'Naval base', 'O': 'Naval outpost',
                    'R': 'Clan base', 'S': 'Scout base', 'T': 'Tlaukhu base', 'V': 'Scout base', 'W': 'Way station',
                    '*': 'Unknown', 'I': 'Unknown',
                    'G': 'Vargr Naval base', 'J': 'Naval base',
                    'L': 'Hiver naval base', 'P': 'Droyne Naval base', 'Q': 'Droyne military garrison',
                    'X': 'Zhodani relay station', 'Y': 'Zhodani depot',
                    'A': 'Split', 'B': 'Split', 'F': 'Split', 'H': 'Split', 'U': 'Split', 'Z': 'Split'}

    def __init__(self) -> None:
        self.population = 0
        self.populations = NoNoneDefaultDict(Populations)

        self.economy = 0
        self.trade = 0
        self.tradeExt = 0
        self.tradeVol = 0
        self.tradeDton = 0
        self.tradeDtonExt = 0
        self.percapita = 0
        self.number = 0
        self.milBudget = 0
        self.maxTL = 0
        self.maxPort = 'X'
        self.maxPop = 0
        self.sum_ru = 0
        self.shipyards = 0
        self.col_be = 0
        self.im_be = 0
        self.passengers = 0
        self.spa_people = 0
        self.port_size = NoNoneDefaultDict(int)
        self.code_counts = NoNoneDefaultDict(int)
        self.bases = NoNoneDefaultDict(int)
        self.eti_worlds = 0
        self.eti_cargo = 0
        self.eti_pass = 0
        self.homeworlds: list[Star] = []
        self.high_pop_worlds: list[Star] = []
        self.high_tech_worlds: list[Star] = []
        self.TLmean = 0
        self.TLstddev = 0
        self.subsectorCp: list[Star] = []
        self.sectorCp: list[Star] = []
        self.otherCp: list[Star] = []
        self.gg_count = 0
        self.worlds = 0
        self.stars = 0
        self.star_count = NoNoneDefaultDict(int)
        self.primary_count = NoNoneDefaultDict(int)

    # For the JSONPickel work
    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        for key in ObjectStatistics.__slots__:
            if key not in state:
                state[key] = self[key]
        del state['high_pop_worlds']
        del state['high_tech_worlds']
        del state['subsectorCp']
        del state['sectorCp']
        del state['otherCp']
        del state['homeworlds']
        return state

    def __deepcopy__(self, memodict: dict = {}):
        state = self.__dict__.copy()
        foo = ObjectStatistics()
        foo.__dict__.update(state)
        for key in ObjectStatistics.__slots__:
            if '__dict__' != key:
                with contextlib.suppress(AttributeError):
                    foo[key] = copy.deepcopy(self[key])

        return foo

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __hash__(self) -> int:
        return 0

    def __eq__(self, y) -> bool:
        if not isinstance(y, ObjectStatistics):
            return False
        if self.maxTL != y.maxTL:
            return False
        if self.TLmean != y.TLmean:
            return False
        if self.TLstddev != y.TLstddev:
            return False
        if self.maxPop != y.maxPop:
            return False
        if self.maxPort != y.maxPort:
            return False
        if self.trade != y.trade:
            return False
        if self.tradeExt != y.tradeExt:
            return False
        if self.tradeDton != y.tradeDton:
            return False
        if self.tradeDtonExt != y.tradeDtonExt:
            return False
        return self.tradeVol == y.tradeVol

    def homeworld_count(self) -> int:
        return len(self.homeworlds)

    def high_pop_worlds_count(self) -> int:
        return len(self.high_pop_worlds)

    def high_pop_worlds_list(self) -> list[str]:
        return [world.wiki_name() for world in self.high_pop_worlds[0:6]]

    def high_tech_worlds_count(self) -> int:
        return len(self.high_tech_worlds)

    def high_tech_worlds_list(self) -> list[str]:
        return [world.wiki_name() for world in self.high_tech_worlds[0:6]]

    def populations_count(self) -> int:
        return len(self.populations)

    @property
    def sum_ru_int(self) -> int:
        return int(self.sum_ru)

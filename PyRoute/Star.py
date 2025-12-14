"""
Created on Mar 5, 2014

@author: tjoneslo
"""
import copy
import functools
import logging
import bisect
import random

from typing import Tuple, Optional
from typing_extensions import TypeAlias

from PyRoute.Position.Hex import Hex

from PyRoute.Allies.AllyGen import AllyGen
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.SystemData.Utilities import Utilities

from PyRoute.SystemData.StarList import StarList

HexPos: TypeAlias = Tuple[int, int]


class Star(object):
    __slots__ = '__dict__', 'worlds', 'ggCount', 'belts', 'nobles', 'logger', '_hash', '_key', 'component', 'index',\
                'gwp', 'population', 'perCapita', 'mspr', 'wtn', 'ru', 'ownedBy', 'name', 'sector', 'position', 'uwp',\
                'popM', 'uwpCodes', 'tradeCode', 'economics', 'social', 'baseCode', 'zone', 'alg_code',\
                'allegiance_base', 'alg_base_code', 'ship_capacity', 'tcs_gwp', 'budget', 'importance', 'eti_cargo',\
                'eti_passenger', 'raw_be', 'im_be', 'col_be', 'star_list_object', 'routes', 'stars', 'is_enqueued',\
                'is_target', 'is_landmark', '_pax_btn_mod', 'suppress_soph_percent_warning', 'is_redzone', 'hex',\
                'deep_space_station', '_oldskool', 'tradeIn', 'tradeOver', 'tradeCount', 'passIn', 'passOver',\
                'starportSize', 'starportBudget', 'starportPop', 'index', 'trade_cost', 'trade_id', 'eti_cargo_volume',\
                'eti_worlds', 'eti_pass_volume'

    def __init__(self):
        self.worlds = None
        self.ggCount = None
        self.belts = None
        self.nobles = None
        self.logger = logging.getLogger('PyRoute.Star')
        self._hash = None
        self._key = None
        self.component = None
        self.index = None
        self.gwp = None
        self.population = None
        self.perCapita = None
        self.mspr = None
        self.wtn = None
        self.ru = None
        self.ownedBy = None
        self.name = None
        self.sector = None
        self.position = None
        self.uwp = None
        self.popM = None
        self.uwpCodes = None
        self.tradeCode = None
        self.economics = None
        self.social = None
        self.baseCode = None
        self.zone = None
        self.alg_code = None
        self.allegiance_base = None
        self.alg_base_code = None
        self.ship_capacity = None
        self.tcs_gwp = None
        self.budget = None
        self.importance = None
        self.eti_cargo = None
        self.eti_passenger = None
        self.eti_cargo_volume = None
        self.eti_worlds = None
        self.eti_pass_volume = None
        self.raw_be = None
        self.im_be = None
        self.col_be = None
        self.star_list_object = None
        self.routes = None
        self.stars = None
        self.is_enqueued = False
        self.is_target = False
        self.is_landmark = False
        self._pax_btn_mod = 0
        self.suppress_soph_percent_warning = False
        # Can this star be unilaterally excluded from routes?
        self.is_redzone = False
        self.hex = None
        self.deep_space_station = False
        self._oldskool = False
        # Generated trade values
        self.tradeIn = None
        self.tradeOver = None
        self.tradeCount = None
        self.trade_cost = 0.0
        self.trade_id = ""
        self.passIn = None
        self.passOver = None
        self.starportSize = None
        self.starportBudget = None
        self.starportPop = None

    def __getstate__(self):
        state = self.__dict__.copy()
        for item in Star.__slots__:
            if item in state:
                continue
            if item.startswith('_'):
                continue
            state[item] = self[item]
        del state['sector']
        del state['logger']
        # del state['_hash']
        if self.ownedBy == self:
            del state['ownedBy']
        return state

    def __deepcopy__(self, memodict: dict = {}):
        state = self.__dict__.copy()
        for item in Star.__slots__:
            if item in state:
                continue
            if item.startswith('_'):
                continue
            state[item] = self[item]

        foo = Star()
        for key in state:
            item = state[key]
            setattr(foo, key, item)
        foo.hex = copy.deepcopy(self.hex)
        foo.calc_hash()

        return foo

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @staticmethod
    def parse_line_into_star(line, sector, pop_code, ru_calc, fix_pop=False):
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        star = Star()
        return ParseStarInput.parse_line_into_star_core(star, line, sector, pop_code, ru_calc, fix_pop=fix_pop)

    def parse_to_line(self) -> str:
        result = str(self.position) + " "
        result += self.name.ljust(20) + " "

        result += str(self.uwp)
        star_list = str(self.star_list_object)
        result += " " + str(self.tradeCode).ljust(38)
        if " " != result[-1]:
            result += " "
        if self.oldskool:  # If Ix, Ex and Cx were all missing on the way _in_, they should be missing on the way _out_
            imp_chunk = ' '
            econ = ' '
            social = ' '
        else:
            imp_chunk = "{ " + str(self.importance) + " }"
            econ = str(self.economics) if self.economics is not None else '-'
            social = str(self.social) if self.social is not None else '-'

        result += imp_chunk.ljust(6) + " " + econ.ljust(7) + " " + social.ljust(6) + " "
        result += str(self.nobles).ljust(4) + " "
        popM = str(Utilities.int_to_ehex(self.popM))
        belts = str(Utilities.int_to_ehex(self.belts))
        ggCount = str(Utilities.int_to_ehex(self.ggCount))
        worlds = str(self.worlds)
        basecode = str(self.baseCode).upper()
        alg_code = str(self.alg_code) if "" != self.alg_code.strip() else "--"

        result += basecode.ljust(2) + " " + str(self.zone).ljust(2) + popM + belts + ggCount + " "
        result += str(worlds).ljust(2) + " " + str(alg_code).ljust(4) + " "
        result += str(star_list).ljust(14) + " " + " ".join(self.routes).ljust(41)

        return result

    def __str__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __repr__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __key(self):
        return self._key

    def __eq__(self, y):
        if not isinstance(y, Star):
            return False
        if self.__hash__() != y.__hash__():
            return False
        return self.__key() == y.__key()

    def __hash__(self):
        return self._hash

    def calc_hash(self) -> None:
        self._key = (self.position, self.name, str(self.uwp), self.sector.name)
        self._hash = hash(self._key)

    def wiki_name(self) -> str:
        # name = u" ".join(w.capitalize() for w in self.name.lower().split())
        return '{{WorldS|' + self.name + '|' + self.sector.sector_name() + '|' + self.position + '}}'

    def wiki_short_name(self) -> str:
        # name = u" ".join(w.capitalize() for w in self.name.lower().split())
        return '{} (world)'.format(self.name)

    def sec_pos(self, sector) -> str:
        if self.sector == sector:
            return self.position
        else:
            return self.sector.name[0:4] + '-' + self.position

    def set_location(self) -> None:
        self.hex = Hex(self.sector, self.position)

    @property
    def x(self) -> int:
        return self.hex.x

    @property
    def y(self) -> int:
        return self.hex.y

    @property
    def z(self) -> int:
        return self.hex.z

    @property
    def q(self) -> int:
        return self.hex.q

    @property
    def r(self) -> int:
        return self.hex.r

    @property
    def col(self) -> int:
        return self.hex.col

    @property
    def row(self) -> int:
        return self.hex.row

    @property
    def port(self) -> str:
        return str(self.uwp.port)

    @port.setter
    def port(self, value) -> None:
        self.uwp.port = str(value)

    @property
    def size(self) -> str:
        return self.uwp.size

    @property
    def atmo(self) -> str:
        return self.uwp.atmo

    @property
    def hydro(self) -> str:
        return self.uwp.hydro

    @property
    def pop(self) -> str:
        return self.uwp.pop

    @property
    def gov(self) -> str:
        return self.uwp.gov

    @property
    def law(self) -> str:
        return self.uwp.law

    @property
    def popCode(self) -> int:
        return int(self.uwp.pop_code)

    @property
    def tl(self) -> int:
        return int(self.uwp.tl_code)

    @tl.setter
    def tl(self, value) -> None:
        self.uwp.tl = value

    @property
    def tl_unknown(self) -> bool:
        return '?' == self.uwp.tl

    @property
    def star_list(self) -> list:
        return self.star_list_object.stars_list

    @property
    def primary_type(self) -> Optional[str]:
        if 0 == len(self.star_list):
            return None
        if self.star_list[0].spectral is not None:
            return self.star_list[0].spectral
        return self.star_list[0].size

    @property
    def oldskool(self) -> bool:
        return self.uwp.oldskool is True

    @functools.cached_property
    def hex_position(self) -> HexPos:
        return self.hex.hex_position()

    def distance(self, star) -> int:
        return Hex.axial_distance(self.hex_position, star.hex_position)

    def subsector(self) -> str:
        subsector = ["ABCD", "EFGH", "IJKL", "MNOP"]
        index_y = (self.col - 1) // 8
        index_x = (self.row - 1) // 10
        return subsector[index_x][index_y]

    def wilderness_refuel(self) -> bool:
        return self.uwpCodes['Hydrographics'] in '23456789A' and self.uwpCodes['Atmosphere'] not in 'ABC'

    def calculate_gwp(self, pop_code) -> None:
        calcGWP = [220, 350, 560, 560, 560, 895, 895, 1430, 2289, 3660, 3660, 3660, 5860, 5860, 9375, 15000, 24400,
                   24400, 39000, 39000]
        # flatGWP = [229, 301, 396, 521, 685, 902, 1186, 1560, 2051, 2698, 3548, 4667, 6138, 8072, 10617, 13964, 18365,
        #           24155, 31769, 41783]
        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]

        if pop_code == 'scaled':
            self.population = (pow(10, self.popCode) * popCodeM[self.popM]) // 1e7  # pragma: no mutate
            self.uwpCodes['Pop Code'] = str(popCodeM[self.popM] // 10)

        elif pop_code == 'fixed':
            self.population = (pow(10, self.popCode) * self.popM) // 1e6  # pragma: no mutate

        elif pop_code == 'benford':
            popCodeRange = [0.243529203, 0.442507049, 0.610740422, 0.756470797, 0.885014099, 1]  # pragma: no mutate

            if self.popM >= 1 and self.popM <= 6:
                popM = popCodeM[self.popM]
            else:
                popM = (bisect.bisect(popCodeRange, random.random()) + 4) * 10  # pragma: no mutate
            self.population = (pow(10, self.popCode) * popM) // 1e7  # pragma: no mutate
            self.uwpCodes['Pop Code'] = str(popM / 10)

        self.perCapita = calcGWP[min(self.tl, 19)] if self.population > 0 else 0
        self.perCapita *= 1.6 if self.tradeCode.rich else 1
        self.perCapita *= 1.4 if self.tradeCode.industrial else 1
        self.perCapita *= 1.2 if self.tradeCode.agricultural else 1
        self.perCapita *= 0.8 if self.tradeCode.low_per_capita_gwp else 1

        self.gwp = int((self.population * self.perCapita) // 1000)  # pragma: no mutate
        self.population = int(self.population)
        self.perCapita = int(self.perCapita)

    def calculate_mspr(self) -> None:
        self.mspr = 9

        if self.atmo in ['0', '1', '2', '3', 'A', 'B', 'C']:
            self.mspr = 0
        else:
            self.mspr -= 2 if self.size in ['0', '1'] else 0
            self.mspr -= 1 if self.size in ['2', '3', '4'] else 0
            self.mspr -= 1 if self.hydro in ['1', '2', 'A'] else 0
            self.mspr -= 2 if self.hydro in ['0'] else 0
            self.mspr -= 1 if self.atmo in ['4', '5', '8', '9'] else 0  # thin or dense
            self.mspr -= 1 if self.atmo in ['4', '7', '9'] else 0  # polluted

    def calculate_wtn(self) -> None:
        self.wtn = self.popCode
        self.wtn -= 1 if self.tl == 0 else 0
        self.wtn += 1 if self.tl >= 5 else 0
        self.wtn += 1 if self.tl >= 9 else 0
        self.wtn += 1 if self.tl >= 15 else 0

        port = self.port

        if port == 'A':
            self.wtn = (self.wtn * 3 + 13) // 4
        if port == 'B':
            self.wtn = (self.wtn * 3 + 11) // 4
        if port == 'C':
            self.wtn = min((self.wtn + 9) // 2, (self.wtn * 3 + 9) // 4)
        if port == 'D':
            self.wtn = min((self.wtn + 7) // 2, (self.wtn * 3 + 7) // 4)
        if port == 'E':
            self.wtn = min((self.wtn + 5) // 2, (self.wtn * 3 + 5) // 4)
        if port == 'X':
            self.wtn = (self.wtn - 5) // 2

        self.wtn = max(0, self.wtn)

    def check_ex(self) -> None:
        if not self.economics:
            return

        labor = self._ehex_to_int(self.economics[2])
        infrastructure = self._ehex_to_int(self.economics[3])

        if labor != max(self.popCode - 1, 0):
            self.logger.warning('{} - EX Calculated labor {} does not match generated labor {}'.format(self, labor, max(
                self.popCode - 1, 0)))

        if self.tradeCode.barren and infrastructure != 0:
            self.logger.warning(
                '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.
                format(self, infrastructure, 0))
        elif self.tradeCode.low and infrastructure != max(self.importance, 0):
            self.logger.warning(
                '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.
                format(self, infrastructure, max(self.importance, 0)))
        elif self.tradeCode.nonindustrial and not 0 <= infrastructure <= 6 + self.importance:
            self.logger.warning(
                '{} - EX Calculated infrastructure {} not in NI range 0 - {}'.
                format(self, infrastructure, 6 + self.importance))
        elif not 0 <= infrastructure <= 12 + self.importance:
            self.logger.warning('{} - EX Calculated infrastructure {} not in range 0 - {}'.
                                format(self, infrastructure, 12 + self.importance))

    def fix_ex(self) -> None:
        if not self.economics:
            return

        resources = self._ehex_to_int(self.economics[1])
        labor = self._ehex_to_int(self.economics[2])
        infrastructure = self._ehex_to_int(self.economics[3])
        efficiency = self._ehex_to_int(self.economics[5])

        if 8 > self.uwp.tl_code:
            nu_resources = self._int_to_ehex(max(0, min(12, resources)))
            self.economics = self.economics[0:1] + nu_resources + self.economics[2:]
        else:
            max_resources = 12 + self.ggCount + self.belts
            nu_resources = self._int_to_ehex(max(0, min(max_resources, resources)))
            self.economics = self.economics[0:1] + nu_resources + self.economics[2:]

        max_labor = max(self.popCode - 1, 0)
        if labor != max_labor:
            nu_labour = self._int_to_ehex(max_labor)
            self.economics = self.economics[0:2] + nu_labour + self.economics[3:]

        max_lo_infrastructure = max(self.importance, 0)
        max_ni_infrastructure = 6 + self.importance
        max_infrastructure = 12 + self.importance
        nu_infrastructure = None
        if self.tradeCode.barren and infrastructure != 0:
            nu_infrastructure = '0'
        elif self.tradeCode.low and infrastructure != max_lo_infrastructure:
            nu_infrastructure = self._int_to_ehex(max_lo_infrastructure)
        elif self.tradeCode.nonindustrial and not 0 <= infrastructure <= max_ni_infrastructure:
            nu_infrastructure = '0' if 0 > infrastructure else self._int_to_ehex(max_ni_infrastructure)
        elif not 0 <= infrastructure <= max_infrastructure:
            nu_infrastructure = '0' if 0 > infrastructure else self._int_to_ehex(max_infrastructure)

        if nu_infrastructure is not None:
            self.economics = self.economics[0:3] + nu_infrastructure + self.economics[4:]

        nu_efficiency = None
        if self.tradeCode.barren:
            nu_efficiency = '0'
        elif efficiency == 0:
            nu_efficiency = '1'

        if nu_efficiency is not None:
            self.economics = self.economics[0:5] + nu_efficiency + self.economics[6:]

    def check_cx(self) -> None:
        if not self.social:
            return
        pop = self.popCode

        homogeneity = self._ehex_to_int(self.social[1])  # pop + flux, min 1
        if pop == 0 and homogeneity != 0:
            self.logger.warning(
                '{} - CX Calculated homogeneity {} should be 0 for barren worlds'.format(self, homogeneity))
        elif pop != 0 and not max(1, pop - 5) <= homogeneity <= pop + 5:
            self.logger.warning(
                '{} - CX Calculated homogeneity {} not in range {} - {}'.
                format(self, homogeneity, max(1, pop - 5), pop + 5))

        acceptance = self._ehex_to_int(self.social[2])  # pop + Ix, min 1
        pop_plus_imp = min(33, max(1, pop + self.importance))  # Cap out at 33 - converts to ehex as Z
        if pop == 0 and acceptance != 0:
            self.logger.warning(
                '{} - CX Calculated acceptance {} should be 0 for barren worlds'.format(self, acceptance))
        elif pop != 0 and pop_plus_imp != acceptance:
            self.logger.warning(
                '{} - CX Calculated acceptance {} does not match generated acceptance {}'.
                format(self, acceptance, pop_plus_imp))

        strangeness = self._ehex_to_int(self.social[3])  # flux + 5
        if pop == 0 and strangeness != 0:
            self.logger.warning(
                '{} - CX Calculated strangeness {} should be 0 for barren worlds'.format(self, strangeness))
        elif pop != 0 and not 1 <= strangeness <= 10:
            self.logger.warning(
                '{} - CX Calculated strangeness {} not in range {} - {}'.format(self, strangeness, 1, 10))

        symbols = self._ehex_to_int(self.social[4])  # TL + flux, min 1
        if pop == 0 and symbols != 0:
            self.logger.warning('{} - CX Calculated symbols {} should be 0 for barren worlds'.format(self, symbols))
        elif pop != 0 and not max(1, self.tl - 5) <= symbols <= self.tl + 5:
            self.logger.warning(
                '{} - CX Calculated symbols {} not in range {} - {}'.
                format(self, symbols, max(1, self.tl - 5), self.tl + 5))

    def fix_cx(self) -> None:
        if not self.social:
            return
        pop = self.popCode

        homogeneity = self._ehex_to_int(self.social[1])
        min_homogeneity = max(1, pop - 5)
        max_homogeneity = pop + 5
        nu_homogeneity = None
        if 0 == pop and 0 != homogeneity:
            nu_homogeneity = '0'
        elif 0 != pop and homogeneity < min_homogeneity:
            nu_homogeneity = self._int_to_ehex(min_homogeneity)
        elif 0 != pop and homogeneity > max_homogeneity:
            nu_homogeneity = self._int_to_ehex(max_homogeneity)

        if nu_homogeneity is not None:
            self.social = self.social[0] + nu_homogeneity + self.social[2:]

        acceptance = self._ehex_to_int(self.social[2])
        nu_acceptance = None
        if 0 == pop and 0 != acceptance:
            nu_acceptance = '0'
        elif 0 != pop and max(1, pop + self.importance) != acceptance:
            nu_acceptance = self._int_to_ehex(max(1, pop + self.importance))

        if nu_acceptance is not None:
            self.social = self.social[0:2] + nu_acceptance + self.social[3:]

        strangeness = self._ehex_to_int(self.social[3])
        nu_strangeness = None
        if 0 == pop and 0 != strangeness:
            nu_strangeness = '0'
        elif 0 != pop and 1 > strangeness:
            nu_strangeness = self._int_to_ehex(1)
        elif 0 != pop and 10 < strangeness:
            nu_strangeness = self._int_to_ehex(10)

        if nu_strangeness is not None:
            self.social = self.social[0:3] + nu_strangeness + self.social[4:]

        symbols = self._ehex_to_int(self.social[4])
        min_symbols = max(1, self.tl - 5)
        max_symbols = self.tl + 5
        nu_symbols = None
        if 0 == pop and symbols != 0:
            nu_symbols = '0'
        elif 0 != pop and symbols < min_symbols:
            nu_symbols = self._int_to_ehex(min_symbols)
        elif 0 != pop and symbols > max_symbols:
            nu_symbols = self._int_to_ehex(max_symbols)

        if nu_symbols is not None:
            self.social = self.social[0:4] + nu_symbols + self.social[5:]

    def fix_tl(self) -> None:
        if self.tl_unknown:  # if TL is unknown, no point canonicalising it
            return

        max_tl, min_tl = ParseStarInput.check_tl_core(self)
        new_tl = max(min_tl, min(max_tl, self.tl))
        self.tl = Utilities.int_to_ehex(new_tl)

    def calculate_ru(self, ru_calc) -> None:
        if not self.economics:
            self.ru = 0
            return

        resources = self._ehex_to_int(self.economics[1])
        labor = self._ehex_to_int(self.economics[2])
        if self.economics[3] == '-':
            infrastructure = self._ehex_to_int(self.economics[3:5])  # pragma: no mutate
            efficiency = float(self.economics[5:7].strip(')'))  # pragma: no mutate
        else:
            infrastructure = self._ehex_to_int(self.economics[3])
            efficiency = float(self.economics[4:6])

        resources = resources if resources != 0 else 1
        # No I in eHex, so J,K,L all -1
        resources -= 0 if resources < 18 else 1

        labor = labor if labor != 0 else 1
        labor = labor if self.popCode != 0 else 0

        infrastructure = infrastructure if infrastructure != 0 else 1
        infrastructure += 0 if infrastructure < 18 else -1

        efficiency = efficiency if efficiency != 0 else 1
        if efficiency < 0 and 'scaled' == ru_calc:
            efficiency = 1.0 + (efficiency * 0.1)
            # else ru_calc == 'negative' -> use efficiency as written

        self.ru = int(round(resources * labor * infrastructure * efficiency))

        self.logger.debug(
            "RU = {0} * {1} * {2} * {3} = {4}".format(resources, labor, infrastructure, efficiency, self.ru))

    def calculate_TCS(self) -> None:
        self.ship_capacity = int(self.population * Utilities.tax_rate[self.uwpCodes['Government']] * 1000)
        gwp_base = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32]
        if self.tl >= 5:
            self.tcs_gwp = self.population * gwp_base[min(self.tl - 5, 13)] * 1000
        else:
            self.tcs_gwp = 0

        if self.tradeCode.rich:
            self.tcs_gwp = self.tcs_gwp * 16 // 10  # pragma: no mutate
        if self.tradeCode.industrial:
            self.tcs_gwp = self.tcs_gwp * 14 // 10  # pragma: no mutate
        if self.tradeCode.agricultural:
            self.tcs_gwp = self.tcs_gwp * 12 // 10  # pragma: no mutate
        if self.tradeCode.poor:
            self.tcs_gwp = self.tcs_gwp * 8 // 10
        if self.tradeCode.nonindustrial:
            self.tcs_gwp = self.tcs_gwp * 8 // 10
        if self.tradeCode.nonagricultural:
            self.tcs_gwp = self.tcs_gwp * 8 // 10

        budget = int(self.tcs_gwp * 0.03 * Utilities.tax_rate[self.uwpCodes['Government']])

        # if AllyGen.sameAligned('Im', self.alg):
        #    budget = budget * 0.3

        transfer_rate = {'A': 1.0, 'B': 0.95, 'C': 0.9, 'D': 0.85, 'E': 0.8}

        if self.uwpCodes['Starport'] in 'ABCDE':
            access = transfer_rate[self.uwpCodes['Starport']]
            access -= (15 - self.tl) * 0.05
            # By the time we reach here, TL < 5 means tcs_gwp is 0, thus budget is zero
            # if self.tl <= 4:
            #     access -= 0.05
            # if self.tl <= 3:
            #     access -= 0.05
        else:
            access = 0

        access = max(0, access)

        self.budget = int(budget * access)

    def calculate_importance(self) -> None:
        imp = 1 if self.port in ['A', 'B'] else 0
        imp -= 1 if self.port in ['D', 'E', 'X'] else 0
        imp -= 1 if self.tl <= 8 else 0
        imp += 1 if self.tl >= 10 else 0
        imp += 1 if self.tl >= 16 else 0
        imp -= 1 if self.popCode <= 6 else 0
        imp += 1 if self.popCode >= 9 else 0
        imp += 1 if self.tradeCode.agricultural else 0
        imp += 1 if self.tradeCode.rich else 0
        imp += 1 if self.tradeCode.industrial else 0
        imp += 1 if self.baseCode in ['NS', 'NW', 'W', 'D', 'X', 'KV', 'RT', 'CK', 'KM'] else 0
        self.importance = imp

    def calculate_eti(self) -> None:
        eti = 1 if self.port in ['A', 'B'] else 0
        eti -= 1 if self.port in ['D', 'E', 'X'] else 0
        eti += 1 if self.tl >= 10 else 0
        eti -= 1 if self.tl <= 7 else 0
        eti += 1 if self.baseCode in ['NS', 'NW', 'D', 'X', 'KV', 'RT', 'CK', 'KM'] else 0
        eti += 1 if self.tradeCode.capital else 0
        eti += 1 if self.tradeCode.agricultural else 0
        eti += 1 if self.tradeCode.rich else 0
        eti += 1 if self.tradeCode.industrial else 0
        eti -= 1 if self.tradeCode.poor else 0
        eti -= 1 if self.popCode <= 3 else 0
        eti += 1 if self.popCode >= 9 else 0
        eti -= 1 if self.zone in ['A', 'U'] else 0
        eti -= 8 if self.zone in ['R', 'F'] else 0
        self.eti_cargo = eti
        eti -= 1 if self.baseCode in ['NS', 'NW', 'D', 'X', 'KV', 'RT', 'CK', 'KM'] else 0
        eti -= 1 if self.tradeCode.agricultural else 0
        eti -= 2 if self.tradeCode.industrial else 0
        eti -= 1 if self.zone in ['A', 'U'] else 0
        self.eti_passenger = eti

    def calculate_army(self) -> None:
        #       3, 4, 5, 6, 7, 8, 9, A

        BE = [[0, 0, 0, 0, 1, 10, 100, 1000],  # TL 0
              [0, 0, 0, 1, 5, 50, 500, 5000],  # TL 1
              [0, 0, 1, 5, 50, 500, 5000, 50000],  # TL 2
              [0, 1, 10, 100, 1000, 10000, 50000, 100000],  # TL 3
              [0, 1, 10, 100, 1000, 2000, 20000, 200000],  # TL 4
              [1, 2, 3, 30, 300, 3000, 30000, 300000],  # TL 5
              [1, 2, 3, 30, 300, 3000, 30000, 300000],  # TL 6
              [0, 1, 2, 20, 200, 2000, 20000, 200000],  # TL 7
              [0, 1, 2, 20, 200, 2000, 20000, 200000],  # TL 8
              [0, 0, 1, 15, 150, 1500, 15000, 150000],  # TL 9
              [0, 0, 1, 15, 150, 1500, 15000, 150000],  # TL A
              [0, 0, 1, 12, 120, 1200, 12000, 120000],  # TL B
              [0, 0, 1, 12, 120, 1200, 12000, 120000],  # TL C
              [0, 0, 1, 10, 100, 1000, 10000, 100000],  # TL D
              [0, 0, 0, 7, 70, 700, 7000, 70000],  # TL E
              [0, 0, 0, 5, 50, 500, 5000, 50000],  # TL F
              [0, 0, 0, 5, 50, 500, 5000, 50000],  # TL G
              ]

        pop_code = min(self.popCode - 3, 7)
        if self.uwpCodes['Atmosphere'] not in ['5', '6', '8']:
            pop_code -= 1
        if pop_code >= 0:
            self.raw_be = BE[min(self.tl, 16)][pop_code]
        else:
            self.raw_be = 0

        self.col_be = self.raw_be * 0.1 if self.tl >= 9 else 0

        if AllyGen.imperial_align(self.alg_code):
            self.im_be = self.raw_be * 0.05
            if self.tl < 13:  # pragma: no mutate
                mul = 1 - ((13 - self.tl) / 10.0)
                self.im_be = self.im_be * mul
        else:
            self.im_be = 0

    def _ehex_to_int(self, value):
        return Utilities.ehex_to_int(value)

    def _int_to_ehex(self, value):
        return Utilities.int_to_ehex(value)

    def split_stellar_data(self) -> None:
        self.star_list_object = StarList(self.stars)
        self.star_list_object.move_biggest_to_primary()

    def extract_routes(self) -> None:
        str_split = self.stars.split()
        self.routes = [route for route in str_split if route.startswith('Xb:') or route.startswith('Tr:')]

        start_xb = self.stars.find('Xb:')
        start_tr = self.stars.find('Tr:')

        start_xb = len(self.stars) if start_xb < 0 else start_xb
        start_tr = len(self.stars) if start_tr < 0 else start_tr

        star_end = min(start_xb, start_tr)

        self.stars = self.stars[0:star_end].strip()
        if len(self.routes) > 0:
            self.logger.debug("{} - routes: {}".format(self, self.routes))

    def is_well_formed(self) -> bool:
        from PyRoute.AreaItems.Sector import Sector
        from PyRoute.SystemData.UWP import UWP
        assert isinstance(self.sector, Sector), "Star " + str(self.name) + " has empty/bad sector attribute"
        assert isinstance(self.index, int), "Star " + str(self.name) + " has empty/bad index attribute"
        assert isinstance(self.hex, Hex), "Star " + str(self.name) + " has empty/bad hex attribute"
        result, msg = self.hex.is_well_formed()
        assert result, msg
        if self.economics is not None:
            assert (isinstance(self.economics, str) and 7 == len(self.economics)),\
                "Star " + str(self.name) + " economics must be None or 7-char string"
        if self.social is not None:
            assert (isinstance(self.social, str) and 6 == len(self.social)),\
                "Star " + str(self.name) + " social must be None or 6-char string"

        assert self.allegiance_base is not None, "Star " + str(self.name) + " has empty base allegiance attribute"
        assert isinstance(self.uwp, UWP), "Star " + str(self.name) + " has empty/bad UWP attribute"
        result, msg = self.uwp.is_well_formed()
        assert result, msg
        assert self.star_list_object is not None, "Star " + str(self.name) + " has empty star_list_object attribute"
        result, msg = self.star_list_object.is_well_formed()
        assert result, msg
        return True

    @property
    def passenger_btn_mod(self) -> int:
        return self._pax_btn_mod

    @property
    def ru_int(self) -> int:
        return int(self.ru)

    def calc_passenger_btn_mod(self) -> None:
        rich = 1 if self.tradeCode.rich else 0
        # Only apply the modifier corresponding to the highest-level capital - other_capital beats sector_capital,
        # which in turn beats subsector_capital.  The current approach makes adding a different value for other_capital
        # (eg 3) very easy.
        capital = 2 if self.tradeCode.sector_capital or self.tradeCode.other_capital else 1 if \
            self.tradeCode.subsector_capital else 0
        self._pax_btn_mod = rich + capital

    def canonicalise(self) -> None:
        self.uwp.canonicalise()
        self.tradeCode.canonicalise(self)
        self.fix_tl()
        self.calculate_importance()
        self.fix_ex()
        self.fix_cx()
        self.star_list_object.canonicalise()
        self.calculate_importance()

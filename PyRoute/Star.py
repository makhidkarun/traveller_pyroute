"""
Created on Mar 5, 2014

@author: tjoneslo
"""
import copy
import logging
import bisect
import random
import math

from PyRoute.Position.Hex import Hex

from PyRoute.AllyGen import AllyGen
from PyRoute.SystemData.Utilities import Utilities
from collections import OrderedDict

from PyRoute.SystemData.StarList import StarList


class UWPCodes(object):
    uwpCodes = ['Starport',
                'Size',
                'Atmosphere',
                'Hydrographics',
                'Population',
                'Government',
                'Law Level',
                'Tech Level',
                'Pop Code',
                'Starport Size',
                'Primary Type',
                'Importance',
                'Resources']

    def __init__(self):
        self.codes = OrderedDict()
        for uwpCode in UWPCodes.uwpCodes:
            self.codes[uwpCode] = "X"


class Star(object):
    __slots__ = '__dict__', '_hash', '_key', 'index', 'zone', 'tradeCode', 'wtn', 'alg_code', 'hex'

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
        self.ship_capacity = None
        self.tcs_gwp = None
        self.budget = None
        self.importance = None
        self.eti_cargo = None
        self.eti_passenger = None
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

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sector']
        del state['logger']
        del state['_hash']
        if self.ownedBy == self:
            del state['ownedBy']
        return state

    def __deepcopy__(self, memodict={}):
        state = self.__dict__.copy()

        foo = Star()
        for key in state:
            item = state[key]
            setattr(foo, key, item)
        foo.index = self.index
        foo.calc_hash()
        foo.hex = copy.deepcopy(self.hex)

        return foo

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    @staticmethod
    def parse_line_into_star(line, sector, pop_code, ru_calc):
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        star = Star()
        return ParseStarInput.parse_line_into_star_core(star, line, sector, pop_code, ru_calc)

    def parse_to_line(self):
        result = str(self.position) + " "
        result += self.name.ljust(20) + " "

        result += str(self.uwp)
        imp_chunk = "{ " + str(self.importance) + " }"
        star_list = str(self.star_list_object)
        result += " " + str(self.tradeCode).ljust(38) + imp_chunk.ljust(6) + " "
        econ = str(self.economics) if self.economics is not None else '-'
        social = str(self.social) if self.social is not None else '-'

        result += econ.ljust(7) + " " + social.ljust(6) + " " + str(self.nobles).ljust(4) + " "
        popM = str(Utilities.int_to_ehex(self.popM))
        belts = str(Utilities.int_to_ehex(self.belts))
        ggCount = str(Utilities.int_to_ehex(self.ggCount))

        result += str(self.baseCode).ljust(2) + " " + str(self.zone).ljust(1) + " " + popM + belts + ggCount + " "
        result += str(self.worlds).ljust(2) + " " + str(self.alg_code).ljust(4) + " "
        result += str(star_list).ljust(14) + " " + " ".join(self.routes).ljust(41)

        return result

    def __unicode__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __str__(self):
        return "%s (%s %s)" % (self.name, self.sector.name, self.position)

    def __repr__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __key(self):
        return self._key

    def __eq__(self, y):
        if self.__hash__() != y.__hash__():
            return False
        if isinstance(y, Star):
            return self.__key() == y.__key()
        else:
            return False

    def __hash__(self):
        return self._hash

    def calc_hash(self):
        self._key = (self.position, self.name, str(self.uwp), self.sector.name)
        self._hash = hash(self._key)

    def wiki_name(self):
        # name = u" ".join(w.capitalize() for w in self.name.lower().split())
        return '{{WorldS|' + self.name + '|' + self.sector.sector_name() + '|' + self.position + '}}'

    def wiki_short_name(self):
        # name = u" ".join(w.capitalize() for w in self.name.lower().split())
        return '{} (world)'.format(self.name)

    def sec_pos(self, sector):
        if self.sector == sector:
            return self.position
        else:
            return self.sector.name[0:4] + '-' + self.position

    def set_location(self):
        self.hex = Hex(self.sector, self.position)

    @property
    def x(self):
        return self.hex.x

    @property
    def y(self):
        return self.hex.y

    @property
    def z(self):
        return self.hex.z

    @property
    def q(self):
        return self.hex.q

    @property
    def r(self):
        return self.hex.r

    @property
    def col(self):
        return self.hex.col

    @property
    def row(self):
        return self.hex.row

    @property
    def port(self):
        return str(self.uwp.port)

    @port.setter
    def port(self, value):
        self.uwp.port = str(value)

    @property
    def size(self):
        return self.uwp.size

    @property
    def atmo(self):
        return self.uwp.atmo

    @property
    def hydro(self):
        return self.uwp.hydro

    @property
    def pop(self):
        return self.uwp.pop

    @property
    def gov(self):
        return self.uwp.gov

    @property
    def law(self):
        return self.uwp.law

    @property
    def popCode(self):
        return int(self.uwp.pop_code)

    @property
    def tl(self):
        return int(self.uwp.tl_code)

    @tl.setter
    def tl(self, value):
        self.uwp.tl = value

    @property
    def star_list(self):
        return self.star_list_object.stars_list

    @property
    def primary_type(self):
        if self.star_list[0].spectral is not None:
            return self.star_list[0].spectral
        return self.star_list[0].size

    def distance(self, star):
        hex1 = self.hex.hex_position()
        hex2 = star.hex.hex_position()

        return Hex.axial_distance(hex1, hex2)

    def subsector(self):
        subsector = ["ABCD", "EFGH", "IJKL", "MNOP"]
        index_y = (self.col - 1) // 8
        index_x = (self.row - 1) // 10
        return subsector[index_x][index_y]

    def calculate_gwp(self, pop_code):
        calcGWP = [220, 350, 560, 560, 560, 895, 895, 1430, 2289, 3660, 3660, 3660, 5860, 5860, 9375, 15000, 24400,
                   24400, 39000, 39000]
        # flatGWP = [229, 301, 396, 521, 685, 902, 1186, 1560, 2051, 2698, 3548, 4667, 6138, 8072, 10617, 13964, 18365,
        #           24155, 31769, 41783]
        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]

        if pop_code == 'scaled':
            self.population = (pow(10, self.popCode) * popCodeM[self.popM]) // 1e7
            self.uwpCodes['Pop Code'] = str(popCodeM[self.popM] // 10)

        elif pop_code == 'fixed':
            self.population = (pow(10, self.popCode) * self.popM) // 1e6

        elif pop_code == 'benford':
            popCodeRange = [0.243529203, 0.442507049, 0.610740422, 0.756470797, 0.885014099, 1]

            if self.popM >= 1 and self.popM <= 6:
                popM = popCodeM[self.popM]
            else:
                popM = (bisect.bisect(popCodeRange, random.random()) + 4) * 10
            self.population = (pow(10, self.popCode) * popM) // 1e7
            self.uwpCodes['Pop Code'] = str(popM / 10)

        self.perCapita = calcGWP[min(self.tl, 19)] if self.population > 0 else 0
        self.perCapita *= 1.6 if self.tradeCode.rich else 1
        self.perCapita *= 1.4 if self.tradeCode.industrial else 1
        self.perCapita *= 1.2 if self.tradeCode.agricultural else 1
        self.perCapita *= 0.8 if self.tradeCode.low_per_capita_gwp else 1

        self.gwp = int((self.population * self.perCapita) // 1000)
        self.population = int(self.population)
        self.perCapita = int(self.perCapita)

    def calculate_mspr(self):
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

    def calculate_wtn(self):
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
            if self.wtn > 9:
                self.wtn = (self.wtn + 9) // 2
            else:
                self.wtn = (self.wtn * 3 + 9) // 4
        if port == 'D':
            if self.wtn > 7:
                self.wtn = (self.wtn + 7) // 2
            else:
                self.wtn = (self.wtn * 3 + 7) // 4
        if port == 'E':
            if self.wtn > 5:
                self.wtn = (self.wtn + 5) // 2
            else:
                self.wtn = (self.wtn * 3 + 5) // 4
        if port == 'X':
            self.wtn = (self.wtn - 5) // 2

        self.wtn = math.trunc(max(0, self.wtn))

    def check_ex(self):
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

    def check_cx(self):
        if not self.economics:
            return
        if not self.social:
            return
        pop = self.popCode

        homogeneity = self._ehex_to_int(self.social[1])  # pop + flux, min 1
        if pop == 0 and homogeneity != 0:
            self.logger.warning(
                '{} - CX calculated homogeneity {} should be 0 for barren worlds'.format(self, homogeneity))
        elif pop != 0 and not max(1, pop - 5) <= homogeneity <= pop + 5:
            self.logger.warning(
                '{} - CX calculated homogeneity {} not in range {} - {}'.
                format(self, homogeneity, max(1, pop - 5), pop + 5))

        acceptance = self._ehex_to_int(self.social[2])  # pop + Ix, min 1
        if pop == 0 and acceptance != 0:
            self.logger.warning(
                '{} - CX calculated acceptance {} should be 0 for barren worlds'.format(self, acceptance))
        elif pop != 0 and not max(1, pop + self.importance) == acceptance:
            self.logger.warning(
                '{} - CX Calculated acceptance {} does not match generated acceptance {}'.
                format(self, acceptance, max(1, pop + self.importance)))

        strangeness = self._ehex_to_int(self.social[3])  # flux + 5
        if pop == 0 and strangeness != 0:
            self.logger.warning(
                '{} - CX calculated strangeness {} should be 0 for barren worlds'.format(self, strangeness))
        elif pop != 0 and not 1 <= strangeness <= 10:
            self.logger.warning(
                '{} - CX calculated strangeness {} not in range {} - {}'.format(self, strangeness, 1, 10))

        symbols = self._ehex_to_int(self.social[4])  # TL + flux, min 1
        if pop == 0 and symbols != 0:
            self.logger.warning('{} - CX calculated symbols {} should be 0 for barren worlds'.format(self, symbols))
        elif pop != 0 and not max(1, self.tl - 5) <= symbols <= self.tl + 5:
            self.logger.warning(
                '{} - CX calculated symbols {} not in range {} - {}'.
                format(self, symbols, max(1, self.tl - 5), self.tl + 5))

    def calculate_ru(self, ru_calc):
        if not self.economics:
            self.ru = 0
            return

        resources = self._ehex_to_int(self.economics[1])
        labor = self._ehex_to_int(self.economics[2])
        if self.economics[3] == '-':
            infrastructure = self._ehex_to_int(self.economics[3:5])
            efficiency = int(self.economics[5:7])
        else:
            infrastructure = self._ehex_to_int(self.economics[3])
            efficiency = int(self.economics[4:6])

        resources = resources if resources != 0 else 1
        # No I in eHex, so J,K,L all -1
        resources -= 0 if resources < 18 else 1

        labor = labor if labor != 0 else 1
        labor = labor if self.popCode != 0 else 0

        infrastructure = infrastructure if infrastructure != 0 else 1
        infrastructure += 0 if infrastructure < 18 else -1

        efficiency = efficiency if efficiency != 0 else 1
        if efficiency < 0:
            if ru_calc == 'scaled':
                efficiency = 1 + (efficiency * 0.1)
            # else ru_calc == 'negative' -> use efficiency as written
            self.ru = int(round(resources * labor * infrastructure * efficiency))
        else:
            self.ru = resources * labor * infrastructure * efficiency

        self.logger.debug(
            "RU = {0} * {1} * {2} * {3} = {4}".format(resources, labor, infrastructure, efficiency, self.ru))

    def calculate_TCS(self):
        tax_rate = {'0': 0.50, '1': 0.8, '2': 1.0, '3': 0.9, '4': 0.85,
                    '5': 0.95, '6': 1.0, '7': 1.0, '8': 1.1, '9': 1.15,
                    'A': 1.20, 'B': 1.1, 'C': 1.2, 'D': 0.75, 'E': 0.75,
                    'F': 0.75,
                    # Aslan Government codes
                    'G': 1.0, 'H': 1.0, 'J': 1.2, 'K': 1.1, 'L': 1.0,
                    'M': 1.1, 'N': 1.2,
                    # Unknown Gov Codes
                    'I': 1.0, 'P': 1.0, 'Q': 1.0, 'R': 1.0, 'S': 1.0, 'T': 1.0,
                    '': 1.0, 'U': 1.0, 'V': 1.0, 'W': 1.0, 'X': 1.0, '?': 0.0
                    }
        self.ship_capacity = int(self.population * tax_rate[self.uwpCodes['Government']] * 1000)
        gwp_base = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32]
        if self.tl >= 5:
            self.tcs_gwp = self.population * gwp_base[min(self.tl - 5, 13)] * 1000
        else:
            self.tcs_gwp = 0

        if self.tradeCode.rich:
            self.tcs_gwp = self.tcs_gwp * 16 // 10
        if self.tradeCode.industrial:
            self.tcs_gwp = self.tcs_gwp * 14 // 10
        if self.tradeCode.agricultural:
            self.tcs_gwp = self.tcs_gwp * 12 // 10
        if self.tradeCode.poor:
            self.tcs_gwp = self.tcs_gwp * 8 // 10
        if self.tradeCode.nonindustrial:
            self.tcs_gwp = self.tcs_gwp * 8 // 10
        if self.tradeCode.nonagricultural:
            self.tcs_gwp = self.tcs_gwp * 8 // 10

        budget = int(self.tcs_gwp * 0.03 * tax_rate[self.uwpCodes['Government']])

        # if AllyGen.sameAligned('Im', self.alg):
        #    budget = budget * 0.3

        transfer_rate = {'A': 1.0, 'B': 0.95, 'C': 0.9, 'D': 0.85, 'E': 0.8}

        if self.uwpCodes['Starport'] in 'ABCDE':
            access = transfer_rate[self.uwpCodes['Starport']]
            access -= (15 - self.tl) * 0.05
            if self.tl <= 4:
                access -= 0.05
            if self.tl <= 3:
                access -= 0.05
        else:
            access = 0

        if access <= 0:
            access = 0

        self.budget = int(budget * access)

    def calculate_importance(self):
        imp = 0
        imp += 1 if self.port in 'AB' else 0
        imp -= 1 if self.port in 'DEX' else 0
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

    def calculate_eti(self):
        eti = 0
        eti += 1 if self.port in 'AB' else 0
        eti -= 1 if self.port in 'DEX' else 0
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

    def calculate_army(self):
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
        if self.uwpCodes['Atmosphere'] not in '568':
            pop_code -= 1
        if pop_code >= 0:
            self.raw_be = BE[min(self.tl, 16)][pop_code]
        else:
            self.raw_be = 0

        self.col_be = self.raw_be * 0.1 if self.tl >= 9 else 0

        if AllyGen.imperial_align(self.alg_code):
            self.im_be = self.raw_be * 0.05
            if self.tl < 13:
                mul = 1 - ((13 - self.tl) / 10.0)
                self.im_be = self.im_be * mul
        else:
            self.im_be = 0

    def _ehex_to_int(self, value):
        return Utilities.ehex_to_int(value)

    def _int_to_ehex(self, value):
        return Utilities.int_to_ehex(value)

    def split_stellar_data(self):
        self.star_list_object = StarList(self.stars)
        self.star_list_object.move_biggest_to_primary()

    def extract_routes(self):
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

    def is_well_formed(self):
        assert hasattr(self, 'sector'), "Star " + str(self.name) + " is missing sector attribute"
        assert self.sector is not None, "Star " + str(self.name) + " has empty sector attribute"
        assert self.index is not None, "Star " + str(self.name) + " is missing index attribute"
        assert self.hex is not None, "Star " + str(self.name) + " is missing hex attribute"
        result, msg = self.hex.is_well_formed()
        assert result, msg
        assert hasattr(self, 'allegiance_base'), "Star " + str(self.name) + " is missing base allegiance attribute"
        assert self.allegiance_base is not None, "Star " + str(self.name) + " has empty base allegiance attribute"
        result, msg = self.uwp.is_well_formed()
        assert result, msg
        assert self.star_list_object is not None, "Star " + str(self.name) + " has empty star_list_object attribute"
        result, msg = self.star_list_object.is_well_formed()
        assert result, msg
        return True

    @property
    def passenger_btn_mod(self):
        return self._pax_btn_mod

    def calc_passenger_btn_mod(self):
        rich = 1 if self.tradeCode.rich else 0
        # Only apply the modifier corresponding to the highest-level capital - other_capital beats sector_capital,
        # which in turn beats subsector_capital.  The current approach makes adding a different value for other_capital
        # (eg 3) very easy.
        capital = 2 if self.tradeCode.sector_capital or self.tradeCode.other_capital else 1 if \
            self.tradeCode.subsector_capital else 0
        self._pax_btn_mod = rich + capital

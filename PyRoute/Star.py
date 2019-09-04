"""
Created on Mar 5, 2014

@author: tjoneslo
"""

import logging
import bisect
import random
import math
import re
from AllyGen import AllyGen
from TradeCodes import TradeCodes
from collections import OrderedDict


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


class Nobles(object):
    def __init__(self):
        self.nobles = {'Knights': 0,
                       'Baronets': 0,
                       'Barons': 0,
                       'Marquis': 0,
                       'Viscounts': 0,
                       'Counts': 0,
                       'Dukes': 0,
                       'Sector Dukes': 0,
                       'Archdukes': 0,
                       'Emperor': 0}
        self.codes = {'B': 'Knights',
                      'c': 'Baronets',
                      'C': 'Barons',
                      'D': 'Marquis',
                      'e': 'Viscounts',
                      'E': 'Counts',
                      'f': 'Dukes',
                      'F': 'Sector Dukes',
                      'G': 'Archdukes',
                      'H': 'Emperor'}

    def __str__(self):
        nobility = ""
        for rank, count in self.nobles.items():
            if count > 0:
                nobility += list(self.codes.keys())[list(self.codes.values()).index(rank)]
        return ''.join(sorted(nobility, key=lambda v: (v.lower(), v[0].isupper())))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['codes']
        return state

    def count(self, nobility):
        for code, rank in self.codes.items():
            if code in nobility:
                self.nobles[rank] += 1

    def accumulate(self, nobles):
        for rank, count in nobles.nobles.items():
            self.nobles[rank] += count


class Star(object):
    regex = """
^(\d\d\d\d) +
(.{15,}) +
(\w\w\w\w\w\w\w-\w|\?\?\?\?\?\?\?-\?) +
(.{15,}) +
((\{ *[+-]?[0-6] ?\}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]| -)|( ) ( ) ( )) +
(\w{1,5}|-| ) +
(\w{1,3}|-|\*) +
(\w|-| ) +
([0-9X?][0-9A-FX?][0-9A-FX?]) +
(\d{1,}| ) +
([A-Z0-9?-][A-Za-z0-9?-]{1,3})
(.*)
"""
    starline = re.compile(''.join([line.rstrip('\n') for line in regex]))

    def __init__(self):
        self.logger = logging.getLogger('PyRoute.Star')
        self._hash = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sector']
        del state['logger']
        del state['_hash']
        if self.ownedBy == self:
            del state['ownedBy']
        return state

    @staticmethod
    def parse_line_into_star(line, sector, pop_code, ru_calc):
        star = Star()
        star.sector = sector
        star.logger.debug(line)
        if Star.starline.match(line):
            data = Star.starline.match(line).groups()
        elif '{Anomaly}' in line:
            star.logger.info("Found anomaly, skipping processing: {}".format(line))
            return None
        else:
            star.logger.error("Unmatched line: {}".format(line))
            return None

        star.logger.debug(data)

        star.position = data[0].strip()
        star.set_location(sector.dx, sector.dy)
        star.name = data[1].strip()

        star.uwp = data[2].strip()
        star.port = star.uwp[0]
        star.size = star.uwp[1]
        star.atmo = star.uwp[2]
        star.hydro = star.uwp[3]
        star.pop = star.uwp[4]
        star.gov = star.uwp[5]
        star.law = star.uwp[6]
        star.tl = star._ehex_to_int(star.uwp[8])
        try:
            star.popCode = star._ehex_to_int(star.pop)
        except ValueError:
            star.popCode = 12

        star.tradeCode = TradeCodes(data[3].strip())
        star.ownedBy = star.tradeCode.owned_by(star)

        star.economics = data[6].strip() if data[6] and data[6].strip() != '-' else None
        star.social = data[7].strip() if data[7] and data[7].strip() != '-' else None

        star.nobles = Nobles()
        star.nobles.count(data[11])

        star.baseCode = data[12].strip()
        star.zone = data[13].strip()
        star.ggCount = int(data[14][2], 16) if data[14][2] not in 'X?' else 0
        star.popM = int(data[14][0]) if data[14][0] not in 'X?' else 0
        star.belts = int(data[14][1], 16) if data[14][1] not in 'X?' else 0

        star.worlds = int(data[15]) if data[15].strip().isdigit() else 0

        star.alg_code = data[16].strip()
        star.alg_base_code = star.alg_code

        star.stars = data[17].strip()
        star.extract_routes()
        star.split_stellar_data()

        star.tradeIn = 0
        star.tradeOver = 0
        star.tradeCount = 0
        star.passIn = 0
        star.passOver = 0
        star.starportSize = 0
        star.starportBudget = 0
        star.starportPop = 0

        star.tradeCode.check_world_codes(star)

        if (data[5]):
            imp = int(data[5][1:-1].strip())
            star.calculate_importance()
            if imp != star.importance:
                star.logger.warning(
                    '{}-{} Calculated importance {} does not match generated importance {}'.format(star, star.baseCode,
                                                                                                    star.importance,
                                                                                                    imp))
        else:
            star.calculate_importance()

        star.uwpCodes = {'Starport': star.port,
                         'Size': star.size,
                         'Atmosphere': star.atmo,
                         'Hydrographics': star.hydro,
                         'Population': star.pop,
                         'Government': star.gov,
                         'Law Level': star.law,
                         'Tech Level': star.uwp[8],
                         'Pop Code': str(star.popM),
                         'Starport Size': star.starportSize,
                         'Primary Type': star.star_list[0][0] if star.star_list else 'X',
                         'Importance': star.importance,
                         'Resources': star._ehex_to_int(star.economics[1]) if star.economics else 0
                         }

        star.check_ex()
        star.check_cx()

        star.calculate_wtn()
        star.calculate_mspr()
        star.calculate_gwp(pop_code)

        star.calculate_TCS()
        star.calculate_army()
        star.calculate_ru(ru_calc)

        star.eti_cargo_volume = 0
        star.eti_pass_volume = 0
        star.eti_cargo = 0
        star.eti_passenger = 0
        star.eti_worlds = 0
        star.calculate_eti()

        star.trade_id = None # Used by the Speculative Trade
        return star

    def __unicode__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __str__(self):
        return "%s (%s %s)" % (self.name, self.sector.name, self.position)

    def __repr__(self):
        return "{} ({} {})".format(self.name, self.sector.name, self.position)

    def __key(self):
        return (self.position, self.name, self.uwp, self.sector.name)

    def __eq__(self, y):
        if isinstance(y, Star):
            if self.__hash__() != y.__hash__():
                return False
            return self.__key() == y.__key()
        else:
            return False

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.__key())
        return self._hash

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

    def set_location(self, dx, dy):
        # convert odd-q offset to cube
        q = int(self.position[0:2]) + dx - 1
        r = int(self.position[2:4]) + dy - 1
        self.x = q
        self.z = r - (q - (q & 1)) // 2
        self.y = -self.x - self.z

        # convert cube to axial
        self.q = self.x
        self.r = self.z

        self.col = q - dx + 1
        self.row = r - dy + 1

    def hex_distance(self, star):
        return max(abs(self.x - star.x), abs(self.y - star.y), abs(self.z - star.z))

    @staticmethod
    def heuristicDistance(star1, star2):
        return max(abs(star1.x - star2.x), abs(star1.y - star2.y), abs(star1.z - star2.z))

    @staticmethod
    def axial_distance(Hex1, Hex2):
        return (abs(Hex1[0] - Hex2[0]) + abs(Hex1[1] - Hex2[1])
                + abs(Hex1[0] + Hex1[1] - Hex2[0] - Hex2[1])) // 2

    def distance(self, star):
        y1 = self.y * 2
        if not self.x % 2:
            y1 += 1
        y2 = star.y * 2
        if not star.y % 2:
            y2 += 1
        dy = y2 - y1
        if dy < 1:
            dy = -dy
        dx = star.x - self.x
        if dx < 1:
            dx = -dx
        if dx > dy:
            return dx
        return dx + dy // 2

    def subsector(self):
        subsector = ["ABCD", "EFGH", "IJKL", "MNOP"]
        indexy = (self.col - 1) // 8
        indexx = (self.row - 1) // 10
        return subsector[indexx][indexy]

    def calculate_gwp(self, pop_code):
        calcGWP = [220, 350, 560, 560, 560, 895, 895, 1430, 2289, 3660, 3660, 3660, 5860, 5860, 9375, 15000, 24400,
                   24400, 39000, 39000]
        flatGWP = [229, 301, 396, 521, 685, 902, 1186, 1560, 2051, 2698, 3548, 4667, 6138, 8072, 10617, 13964, 18365,
                   24155, 31769, 41783]
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
        self.perCapita *= 0.8 if self.tradeCode.extreme or \
                                 self.tradeCode.poor or self.tradeCode.nonindustrial or self.tradeCode.low else 1

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
            if (self.wtn > 9):
                self.wtn = (self.wtn + 9) // 2
            else:
                self.wtn = (self.wtn * 3 + 9) // 4
        if port == 'D':
            if (self.wtn > 7):
                self.wtn = (self.wtn + 7) // 2
            else:
                self.wtn = (self.wtn * 3 + 7) // 4
        if port == 'E':
            if (self.wtn > 5):
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
                '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self,
                                                                                                          infrastructure,
                                                                                                          0))
        elif self.tradeCode.low and infrastructure != 1:
            self.logger.warning(
                '{} - EX Calculated infrastructure {} does not match generated infrastructure {}'.format(self,
                                                                                                          infrastructure,
                                                                                                          1))
        elif self.tradeCode.nonindustrial and not 0 <= infrastructure <= 6 + self.importance:
            self.logger.warning(
                '{} - EX Calculated infrastructure {} not in NI range 0 - {}'.format(self, infrastructure,
                                                                                      6 + self.importance))
        elif not 0 <= infrastructure <= 12 + self.importance:
            self.logger.warning('{} - EX Calculated infrastructure {} not in range 0 - {}'.format(self, infrastructure,
                                                                                                 12 + self.importance))

    def check_cx(self):
        if not self.economics:
            return
        pop = self.popCode

        homogeneity = self._ehex_to_int(self.social[1])  # pop + flux, min 1
        if pop == 0 and homogeneity != 0:
            self.logger.warning(
                '{} - CX calculated homogeneity {} should be 0 for barren worlds'.format(self, homogeneity))
        elif pop != 0 and not max(1, pop - 5) <= homogeneity <= pop + 5:
            self.logger.warning(
                '{} - CX calculated homogeneity {} not in range {} - {}'.format(self, homogeneity, max(1, pop - 5),
                                                                                 pop + 5))

        acceptance = self._ehex_to_int(self.social[2])  # pop + Ix, min 1
        if pop == 0 and acceptance != 0:
            self.logger.warning(
                '{} - CX calculated acceptance {} should be 0 for barren worlds'.format(self, acceptance))
        elif pop != 0 and not max(1, pop + self.importance) == acceptance:
            self.logger.warning(
                '{} - CX Calculated acceptance {} does not match generated acceptance {}'.format(self, acceptance,
                                                                                                  max(1,
                                                                                                      pop + self.importance)))

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
                '{} - CX calculated symbols {} not in range {} - {}'.format(self, symbols, max(1, self.tl - 5),
                                                                             self.tl + 5))

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
                    '': 1.0,  'U': 1.0, 'V': 1.0, 'W': 1.0, 'X': 1.0, '?': 0.0
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
        val = int(value, 36) if value in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' else 0
        val -= 1 if val > 18 else 0
        return val

    def split_stellar_data(self):
        starparts = self.stars.split()
        stars = []

        if len(starparts) == 1:
            stars = starparts
        else:
            for (prev, current) in zip([None] + starparts[:-1], starparts):
                if prev in [None, 'V', 'IV', 'Ia', 'Ib', 'II', 'III']:
                    continue
                if prev in ['D']:
                    stars.append(prev)
                else:
                    stars.append(' '.join((prev, current)))
        self.star_list = stars

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

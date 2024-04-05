"""
Created on Mar 26, 2014

@author: tjoneslo
"""
import functools
import logging
from operator import itemgetter
from collections import defaultdict
import os

from PyRoute.Position.Hex import Hex


class AllyGen(object):
    """
    classdocs
    """
    noOne = ['--', '----', '??', 'Xx']
    nonAligned = ['Na', 'Ns', 'Va', 'Cs', 'Hc', 'Kc',
                  'NaHu', 'NaHv', 'NaDr', 'NaVa', 'NaAs', 'NaXx', 'NaXX', "NaSo", "NaZh",
                  'VaEx',
                  'CsCa', 'CsHv', 'CsIm', 'CsMP', 'CsVa', 'CsZh', 'CsRe', 'CsMo', 'CsRr', "CsTw",
                  'Wild']
    sameAligned = [('Im', 'ImAp', 'ImDa', 'ImDc', 'ImDd', 'ImDg', 'ImDi', 'ImDs', 'ImDv',
                    'ImLa', 'ImLc', 'ImLu', 'ImSy', 'ImVd'),
                   ('As', 'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8',
                    'A9', 'TE', 'Of', 'If',
                    'AsIf', 'AsMw', 'AsOf', 'AsSc', 'AsSF', 'AsT0', 'AsT1', 'AsT2',
                    'AsT3', 'AsT4', 'AsT5', 'AsT6', 'AsT7', 'AsT8', 'AsT9', 'AsTA',
                    'AsTv', 'AsTz', 'AsVc', 'AsWc', 'AsXX'),
                   ('Hv', 'HvFd', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H?', 'Hf'),
                   ('JP', 'J-', 'Jh', 'Hl', 'JuPr',
                    'JAOz', 'JAsi', 'JCoK', 'JHhk', 'JLum', 'JMen',
                    'JPSt', 'JRar', 'JUkh', 'JuHl', 'JuRu', 'JVug'),
                   ('Ke', 'KoEm'),
                   ("K1",),
                   ("K2",),
                   ("K3",),
                   ("K4",),
                   ("KC",),
                   ("Kk", "KkTw", "KO"),
                   ('So', 'SoCf', 'SoBF', 'SoCT', 'SoFr', 'SoHn', 'SoKv', 'SoNS',
                    'SoQu', 'SoRD', 'SoRz', 'SoWu'),
                   ('Lp', 'CoLp'),
                   ('Vd', 'VDeG'),
                   ('Vo', 'VOpA'),
                   ('Vx', 'VAsP'),
                   ('V9', 'VInL'),
                   ('Zh', 'ZhAx', 'ZhCa', 'ZhCh', 'ZhCo', 'ZhIa', 'ZhIN',
                    'ZhJp', 'ZhMe', 'ZhOb', 'ZhSh', 'ZhVQ')]

    default_population = {
        "As": "Asla",
        "Cr": "Huma",
        "Dr": "Droy",
        "Hv": "Hive",
        "JP": "Huma",
        "Kk": "KXkr",
        "Pd": "Piri",
        "Te": "Piri",
        "Tk": "Piri",
        "TY": "Drak",
        "Va": "Varg",
        "Vb": "Varg",
        "Vc": "Varg",
        "Wc": "Droy",
        "Yt": "Yask",
        "Zh": "Zhod",
        "AkUn": "Akee",
        "AlCo": "Muri",
        "CAEM": "Esly",
        "CAKT": "Varg",
        "CoLp": "Jend",
        "DaCf": "Dary",
        "FlLe": "Flor",
        "GeOr": "Ormi",
        "GlEm": "Asla",
        "GnCl": "Gnii",
        "IHPr": "Sred",
        "ImLu": "Luri",
        "ImVd": "Vega",
        "IsDo": "Ysla",
        "KaWo": "Karh",
        "KhLe": "Sydi",
        "KoEm": "Jaib",
        "KrPr": "Krot",
        "MaEm": "Mask",
        "MaPr": "MalX",
        "NaAs": "Asla",
        "NaDr": "Droy",
        "NaHv": "Hive",
        "NaVa": "Varg",
        "OcWs": "Stal",
        "SELK": "Lith",
        "SaCo": "Vlaz",
        "Sark": "Varg",
        "SwFW": "Swan",
        "VaEx": "Varg",
        "ZhAx": "Adda",
        "ZhCa": "Vlaz"
    }

    alleg_border_colours = {
        "Im": "red",
        "As": "yellow",
        "Cr": "gold",
        "Dr": None,
        "Hv": "violet",
        "JP": "blue",
        "Kr": "blue",
        "K1": "emerald",
        "K2": "emerald",
        "K3": "emerald",
        "K4": "darkolive",
        "KC": "emerald",
        "Kk": "green",
        "Rr": "blue",
        "So": "orange",
        "TY": "purple",
        "Va": "olive",
        "Vb": "olive",
        "Vc": "olive",
        "Wc": "lightblue",
        "Zh": "blue",
        "--": None,
        "Na": None,
        "----": None,
        "NaHu": None,
        "NaXX": None,
        "NaZh": None,
        "CsIm": None,
        "DaCf": "lightblue",
        "SwCf": "blue",
        "VAug": "olive",
        "VDzF": "olive",
        "NONE": "white",  # Default color
    }

    def __init__(self, galaxy):
        """
        Constructor
        """
        self.galaxy = galaxy
        self.borders = {}  # 2D array using (q,r) as key, with flags for data
        self.borders_map = {}  # 2D array using (q,r) as key, with flags for data, linking borders and hex-map
        self.allyMap = {}  # 2D array using (q,r) as key, with allegiance code as data
        self.logger = logging.getLogger('PyRoute.AllyGen')

    @staticmethod
    def is_unclaimed(alg):
        return alg in AllyGen.noOne

    @staticmethod
    def is_nonaligned(alg, strict=False):
        if strict:
            return alg in AllyGen.nonAligned
        return alg in AllyGen.nonAligned or alg in AllyGen.noOne

    @staticmethod
    def is_wilds(alg):
        return alg.code[0:2] == 'Na' or alg.code in ['Wild', 'VaEx', 'Va']

    @staticmethod
    def is_client_state(alg):
        return alg.code[0:2] == 'Cs'

    @staticmethod
    def same_align(alg):
        for sameAlg in AllyGen.sameAligned:
            if alg in sameAlg:
                return sameAlg[0]
        return alg

    @staticmethod
    def imperial_align(alg):
        return AllyGen.same_align(alg) == 'Im'

    @staticmethod
    def same_align_name(alg, alg_name):
        if alg in AllyGen.nonAligned:
            return alg_name
        else:
            return alg_name.split(',')[0].strip()

    @staticmethod
    def population_align(alg, name):
        # Try getting the default cases
        code = AllyGen.default_population.get(alg, AllyGen.default_population.get(AllyGen.same_align(alg), None))

        # Handle the special cases.
        if code is None:
            if alg[0] == 'V':
                code = "Varg"
            elif alg == 'Na':
                if 'Hiver' in name:
                    code = 'Hive'
                elif 'Vargr' in name:
                    code = 'Varg'
                elif 'Zhodani' in name:
                    code = 'Zhod'
                elif 'Human' in name:
                    code = 'Huma'
                else:
                    code = 'Huma'
            elif alg == 'CsHv':
                code = "Hive"
            elif alg == "CsAs":
                code = "Asla"
            else:
                code = "Huma"
        return code

    @staticmethod
    def sort_allegiances(alg_list, base_match_only):
        # The logic: 
        # base_match_only == true -> --ally-match=collapse
        # only what matches the base allegiances
        # base_match_only == false -> --ally-match=separate
        # want the non-base code or the base codes for single code allegiances. 

        if base_match_only:
            algs = [alg for alg in list(alg_list.values()) if alg.base]
        else:
            base_algs = [alg for alg in list(alg_list.values()) if alg.base]
            detail_algs = [alg for alg in list(alg_list.values()) if not alg.base]

            for alg in detail_algs:
                base_alg = alg_list[AllyGen.same_align(alg.code)]
                if base_algs and base_alg in base_algs:
                    base_algs = base_algs.remove(base_alg)

            algs = detail_algs
            algs += base_algs if base_algs else []
        algs.sort(key=lambda alg: alg.stats.number, reverse=True)
        return algs

    def create_borders(self, match, enforce=True):
        """
            Create borders around various allegiances, Algorithm one.
            From the nroute.c generation system. Every world controls a
            two hex radius. Where the allegiances are the same, the area
            of control is contiguous. Every Non-aligned world is independent
        """
        self.logger.info('Processing worlds for border drawing')
        for star in self.galaxy.star_mapping.values():
            alg = star.alg_code
            # Skip the non-entity worlds
            if AllyGen.is_unclaimed(alg):
                continue
            # Collapse non-aligned into each their own
            if AllyGen.is_nonaligned(alg):
                alg = self.nonAligned[0]
            # Collapse same Aligned into one
            alg = self._collapse_allegiance_if_needed(alg, match)

            self.allyMap[(star.q, star.r)] = alg

        # self._output_map(allyMap, 0)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 1)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 2)

        self._generate_borders(self.allyMap, enforce)

    def _generate_borders(self, allyMap, enforce=True):
        """
        This is deep, dark magic.  Futzing with this will break the border drawing process.

        Convert the allyMap, which is a dict of (q,r) keys with allegiance codes
        as values, into the borders, which is a dict of (q.r) keys with flags
        indicating which side of the hex needs to have a border drawn on:
        1: top or bottom
        2: upper left or upper right
        4: lower left or lower right

        This is a bit of a mess because the line drawing in HexMap is a little strange,
        So the complexity is here to make the draw portion quick.
        """
        for cand_hex in list(allyMap.keys()):
            odd_q = cand_hex[0] & 1
            if self._set_border(allyMap, cand_hex, 2):  # up
                neighbor = Hex.get_neighbor(cand_hex, 2)
                self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | Hex.BOTTOM
                self.borders_map[neighbor] = self.borders_map.setdefault(neighbor, 0) | Hex.BOTTOM
            if self._set_border(allyMap, cand_hex, 5):  # down
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOM
                self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOM
            if self._set_border(allyMap, cand_hex, 1):  # upper right
                neighbour = Hex.get_neighbor(cand_hex, 1)
                self.borders[neighbour] = self.borders.setdefault(neighbour, 0) | Hex.BOTTOMLEFT

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
            if self._set_border(allyMap, cand_hex, 3):  # upper left
                neighbour = Hex.get_neighbor(cand_hex, 3)
                self.borders[neighbour] = self.borders.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                neighbour = cand_hex if odd_q else Hex.get_neighbor(cand_hex, 2)

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
            if self._set_border(allyMap, cand_hex, 0):  # down right
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOMRIGHT
                neighbour = Hex.get_neighbor(cand_hex, 1) if odd_q else Hex.get_neighbor(cand_hex, 0)

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
            if self._set_border(allyMap, cand_hex, 4):  # down left
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOMLEFT

                if odd_q:
                    self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOMLEFT
                else:
                    self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOMRIGHT

        if enforce:
            result, msg = self.is_well_formed()
            assert result, msg

    @staticmethod
    def _set_border(allyMap, cand_hex, direction):
        """
        Determine if the allegiance is different in the direction,
        hence requiring adding a border to the map.
        returns True if border needed, False if not
        """
        neighbor = Hex.get_neighbor(cand_hex, direction)
        # if this is a non-aligned controlled hex,
        # and the neighbor has no setting ,
        # or the neighbor is aligned 
        # Then no border .
        cand_hex_not_aligned = (AllyGen.is_nonaligned(allyMap[cand_hex], True) or allyMap[cand_hex] is None)
        neighbour_is_aligned = (allyMap.get(neighbor, True) or allyMap.get(neighbor, None) not in AllyGen.nonAligned)
        if cand_hex_not_aligned and neighbour_is_aligned:
            return False
        # If not matched allegiance, need a border.
        elif allyMap[cand_hex] != allyMap.get(neighbor, None):
            return True
        return False

    @staticmethod
    def step_map(allyMap):
        newMap = {}
        for cand_hex in allyMap.keys():
            AllyGen._check_direction(allyMap, cand_hex, newMap)
        return newMap

    @staticmethod
    def _check_direction(allyMap, cand_hex, newMap):
        newMap[cand_hex] = allyMap[cand_hex]
        for direction in range(6):
            neighbor = Hex.get_neighbor(cand_hex, direction)
            if neighbor not in allyMap:
                newMap[neighbor] = allyMap[cand_hex]

    def _output_map(self, allyMap, stage):
        path = os.path.join(self.galaxy.output_path, 'allyMap%s.txt' % stage)
        with open(path, "wb") as f:
            for key, value in allyMap.items():
                f.write("{}-{}: border: {}\n".format(key[0], key[1], value))

    @staticmethod
    def are_owned_allies(alg1, alg2):
        """
        Public function to determine if the Allegiances of two
        world are considered allied for the owned world checks.
        """
        if alg1 is None or alg2 is None:
            return False
        if alg1 in AllyGen.noOne or alg2 in AllyGen.noOne:
            return False
        if alg1 == alg2:
            return True
        for sameAlg in AllyGen.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        return False

    @staticmethod
    @functools.cache
    def are_allies(alg1, alg2):
        """
        Public function to determine if the Allegiance of two
        worlds are considered allied for trade purposes or not.
        """
        if alg1 is None or alg2 is None:
            return False
        if alg1 in AllyGen.noOne or alg2 in AllyGen.noOne:
            return False
        if alg1 in AllyGen.nonAligned or alg2 in AllyGen.nonAligned:
            return False
        if alg1 == alg2:
            return True
        for sameAlg in AllyGen.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        return False

    def create_ally_map(self, match, enforce=True):
        """
            Create borders around various allegiances, Algorithm Two.
            From the AllyGen http://dotclue.org/t20/ code created by J. Greely.
            Each world is given a radius of area to claim based upon starport.
            Overlapping claims are resolved to a single claim
            Edges of the map are sliced down.
        """
        self.logger.info('Processing worlds for ally map drawing')

        self.allyMap = self._ally_map(match)
        # self._output_map(allyMap, 3)
        self._generate_borders(self.allyMap, enforce)

    def _ally_map(self, match):
        # Create list of stars
        allyMap, starMap, stars = self._unpack_stars_and_maps(match)

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            # skip the E/X ports 
            cand_hex = (star.q, star.r)
            alg = starMap[cand_hex]

            if star.port in ['E', 'X']:
                maxRange = 1
            else:
                maxRange = ['D', 'C', 'B', 'A'].index(star.port) + 2
            if AllyGen.is_nonaligned(alg, True):
                maxRange = 2
            for dist in range(maxRange):
                neighbor = Hex.get_neighbor(cand_hex, 4, dist)
                for direction in range(6):
                    for _ in range(dist):
                        star_dist = Hex.axial_distance(cand_hex, neighbor)
                        allyMap[neighbor].add((alg, star_dist))
                        neighbor = Hex.get_neighbor(neighbor, direction)

        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 2: non-aligned worlds at dist 1 get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire. 
        for cand_hex in allyMap.keys():
            if len(allyMap[cand_hex]) == 1:
                allyMap[cand_hex] = allyMap[cand_hex].pop()[0]
            else:
                allyList = sorted([algs for algs in allyMap[cand_hex]], key=itemgetter(1))
                if allyList[0][1] == 0:
                    allyMap[cand_hex] = allyList[0][0]
                else:
                    minDistance = allyList[0][1]
                    allyDist = [algs for algs in allyList if algs[1] == minDistance]
                    if len(allyDist) == 1:
                        allyMap[cand_hex] = allyDist[0][0]
                    else:
                        maxCount = -1
                        maxAlly = None
                        for alg, dist in allyDist:
                            if AllyGen.is_nonaligned(alg, True):
                                maxAlly = alg
                                break
                            if self.galaxy.alg[alg].stats.number > maxCount:
                                maxAlly = alg
                                maxCount = self.galaxy.alg[alg].stats.number
                        allyMap[cand_hex] = maxAlly

        # self._output_map(allyMap, 2)

        # Pass 3: find lonely claimed hexes and remove them
        # Do two passes through the data
        for _ in range(2):
            for cand_hex in allyMap.keys():
                if cand_hex in starMap:
                    continue
                neighborAlgs = defaultdict(int)
                for direction in range(6):
                    neighborAlg = allyMap.get(Hex.get_neighbor(cand_hex, direction), None)
                    neighborAlgs[neighborAlg] += 1

                algList = sorted(iter(neighborAlgs.items()), key=itemgetter(1), reverse=True)
                if len(algList) == 0:
                    allyMap[cand_hex] = None
                elif algList[0][1] >= 1:
                    allyMap[cand_hex] = algList[0][0]
                else:
                    allyMap[cand_hex] = self.nonAligned[0]

        return allyMap

    def create_erode_border(self, match, enforce=True):
        """
        Create borders around various allegiances, Algorithm Three.
        From TravellerMap http://travellermap.com/borders/doc.htm
        """
        self.logger.info('Processing worlds for erode map drawing')
        allyMap, starMap = self._erode_map(match)
        changed = True
        change_count = 0
        while changed:
            if change_count == 100:
                self.logger.error('Change count for map processing exceeded expected value of 100')
                break
            changed, allyMap = self._erode(allyMap, starMap)
            if not changed:
                changed, allyMap = self._break_spans(allyMap, starMap)
            change_count += 1

        self.logger.debug('Change Count: {}'.format(change_count))
        self._build_bridges(allyMap, starMap)

        self.allyMap = allyMap
        self._generate_borders(allyMap, enforce)

    def _erode(self, allyMap, starMap):
        """
        Remove edges.
        """
        newMap = {}
        changed = False

        # Erode, remove empty hex from polity
        # if three contiguous hexes are not aligned

        for cand_hex in allyMap.keys():
            # Worlds keep their allegiances.
            if cand_hex in starMap:
                newMap[cand_hex] = starMap[cand_hex]
                continue

            ally_map_candidate = allyMap[cand_hex]

            # The direction/check combo hits all 6 surrounding hexen up 3 times apiece, and, per profiling, is
            # the heaviest chunk of runtime in the whole method (previously 80%+ of runtime), so it's worth
            # memoising.
            not_ally_neighbours = dict()

            # Check for three continuous empty hexes around this cand_hex
            for direction in range(6):
                # pre-heat not_ally_neighbours
                checkHex = Hex.get_neighbor(cand_hex, direction)
                not_ally_neighbours[direction] = not AllyGen.are_allies(ally_map_candidate, allyMap.get(checkHex, None))

            # Only spin through neighbours if there's 3 or more empty hexen - doing this with 2 or fewer empty
            # hexen is a hiding to nowhere, as 3 continuous empty hexen _can't_ exist
            notCount = 0
            if 2 < sum(not_ally_neighbours.values()):
                for direction in range(6):
                    notCount = 0
                    for check in range(3):
                        if not_ally_neighbours[(direction + check) % 6]:
                            notCount += 1
                    if notCount >= 3:
                        break

            if notCount >= 3:
                changed = True
            else:  # No empty hex in range found, keep allegiance.
                newMap[cand_hex] = ally_map_candidate
        return changed, newMap

    def _break_spans(self, allyMap, starMap):
        """'
        BreakSpans - Find a span of four empty (edge) hexes
        and break the span by setting one to not aligned.
        """
        edgeMap = {}
        changed = False
        # Create the edge map, of hexes on the border
        for cand_hex in allyMap.keys():
            for direction in range(6):
                checkHex = Hex.get_neighbor(cand_hex, direction)
                neighborAlg = allyMap.get(checkHex, None)
                if not AllyGen.are_allies(allyMap[cand_hex], neighborAlg):
                    edgeMap[cand_hex] = allyMap[cand_hex]

        for cand_hex in edgeMap.keys():
            if cand_hex in starMap:
                continue
            for direction in range(6):
                if self._check_aligned(starMap, edgeMap, cand_hex, direction, 1) and \
                        self._check_aligned(starMap, edgeMap, cand_hex, direction, 2) and \
                        self._check_aligned(starMap, edgeMap, cand_hex, direction, 3):
                    checkHex = Hex.get_neighbor(cand_hex, direction, 1)
                    allyMap[checkHex] = None
                    edgeMap[checkHex] = None
                    changed = True
                    break

        return changed, allyMap

    def _check_aligned(self, starMap, edgeMap, cand_hex, direction, distance):
        startAlleg = edgeMap[cand_hex]
        checkHex = Hex.get_neighbor(cand_hex, direction, distance)
        # Occupied hex does not count as aligned for this check
        if checkHex in starMap:
            return False
        checkAlleg = edgeMap.get(checkHex, None)
        return AllyGen.are_allies(startAlleg, checkAlleg)

    def _build_bridges(self, allyMap, starMap):
        """
        Build a bridge between two worlds one hex apart as to avoid
        disrupting contiguous empires.
        """
        for cand_hex in starMap.keys():
            self._search_range(cand_hex, allyMap, starMap)

    def _search_range(self, cand_hex, allyMap, starMap):
        newBridge = None
        checked = []
        for direction in range(6):
            checkHex = Hex.get_neighbor(cand_hex, direction)
            if checkHex in starMap:
                if self.are_allies(starMap[cand_hex], starMap[checkHex]):
                    checked.append(checkHex)
                continue
            if self.are_allies(starMap[cand_hex], allyMap.get(checkHex, None)):
                checked.append(checkHex)
                continue
            for second in range(6):
                searchHex = Hex.get_neighbor(checkHex, second)
                if searchHex in checked:
                    newBridge = None
                    continue
                if searchHex == cand_hex or Hex.axial_distance(searchHex, cand_hex) == 1:
                    continue
                if searchHex in starMap and \
                        self.are_allies(starMap[cand_hex], starMap[searchHex]):
                    newBridge = checkHex
                    checked.append(checkHex)
        if newBridge:
            allyMap[newBridge] = starMap[cand_hex]

    def _erode_map(self, match):
        """
        Generate the initial map of allegiances for the erode map.
        Note: This does not match the original system.
        """
        # Create list of stars
        allyMap, starMap, stars = self._unpack_stars_and_maps(match)

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            cand_hex = (star.q, star.r)
            alg = starMap[cand_hex]

            if AllyGen.is_nonaligned(alg, True):
                maxRange = 0
            elif star.port in ['E', 'X', '?']:
                maxRange = 1
            else:
                maxRange = ['D', 'C', 'B', 'A'].index(star.port) + 2

            # Walk the ring filling in the hexes around star with this neighbor
            for dist in range(1, maxRange):
                # Start in direction 0, at distance n
                neighbor = Hex.get_neighbor(cand_hex, 4, dist)
                # walk six sides
                for side in range(6):
                    for _ in range(dist):
                        allyMap[neighbor].add((alg, Hex.axial_distance(cand_hex, neighbor)))
                        neighbor = Hex.get_neighbor(neighbor, side)
        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire. 
        for cand_hex in allyMap.keys():
            if len(allyMap[cand_hex]) == 1:
                allyMap[cand_hex] = allyMap[cand_hex].pop()[0]
            else:
                allyList = sorted([algs for algs in allyMap[cand_hex]], key=itemgetter(1))
                if allyList[0][1] == 0:
                    allyMap[cand_hex] = allyList[0][0]
                else:
                    minDistance = allyList[0][1]
                    allyDist = [algs for algs in allyList if algs[1] == minDistance]
                    if len(allyDist) == 1:
                        allyMap[cand_hex] = allyDist[0][0]
                    else:
                        maxCount = -1
                        maxAlly = None
                        for alg, dist in allyDist:
                            if not AllyGen.is_nonaligned(alg, True) and \
                                    self.galaxy.alg[alg].stats.number > maxCount:
                                maxAlly = alg
                                maxCount = self.galaxy.alg[alg].stats.number
                        allyMap[cand_hex] = maxAlly

        return allyMap, starMap

    def _unpack_stars_and_maps(self, match):
        stars = self.galaxy.star_mapping.values()
        allyMap = defaultdict(set)
        starMap = {}
        # Mark the map with all the stars
        for star in stars:
            alg = star.alg_code
            # Collapse non-aligned into one value
            if AllyGen.is_nonaligned(alg):
                alg = self.nonAligned[0]

            # Collapse same Aligned into one
            alg = self._collapse_allegiance_if_needed(alg, match)

            allyMap[(star.q, star.r)].add((alg, 0))
            starMap[(star.q, star.r)] = alg
        return allyMap, starMap, stars

    def _collapse_allegiance_if_needed(self, alg, match):
        if 'collapse' == match:
            alg = self.same_align(alg)
        elif 'separate' == match:
            pass
        return alg

    def is_well_formed(self):
        for cand_hex in self.borders:
            border_val = self.borders[cand_hex]
            if border_val & Hex.BOTTOM:  # this hex has a bottom-edge border
                result, msg = self._bottom_left_edge(cand_hex, border_val)
                if not result:
                    return False, msg
                result, msg = self._bottom_right_edge(cand_hex, border_val)
                if not result:
                    return False, msg
            if border_val & Hex.BOTTOMLEFT:  # this hex has a bottom-left border
                result, msg = self._left_left_edge(cand_hex, border_val)
                if not result:
                    return False, msg
                result, msg = self._left_right_edge(cand_hex, border_val)
                if not result:
                    return False, msg
            if border_val & Hex.BOTTOMRIGHT:  # this hex has a bottom-right border
                result, msg = self._right_left_edge(cand_hex, border_val)
                if not result:
                    return False, msg
                result, msg = self._right_right_edge(cand_hex, border_val)
                if not result:
                    return False, msg
        return True, ''

    def _bottom_left_edge(self, cand_hex, border_val):
        msg = ''
        if border_val and Hex.BOTTOMLEFT:
            return True, msg  # bottom edge is left-connected, move on
        neighbour = Hex.get_neighbor(cand_hex, 4)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOMRIGHT:
                return True, msg  # bottom edge is left-connected, move on
        msg = "Bottom edge of " + str(cand_hex) + " is not left-connected"
        return False, msg

    def _bottom_right_edge(self, cand_hex, border_val):
        msg = ''
        if border_val and Hex.BOTTOMRIGHT:
            return True, msg  # bottom edge is right-connected, move on
        neighbour = Hex.get_neighbor(cand_hex, 0)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOMLEFT:
                return True, msg  # bottom edge is right-connected, move on
        msg = "Bottom edge of " + str(cand_hex) + " is not right-connected"
        return False, msg

    def _left_left_edge(self, cand_hex, border_val):
        msg = ''
        neighbour = Hex.get_neighbor(cand_hex, 3)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOM:
                return True, msg  # left edge is left-connected, move on
            if neighbour_val & Hex.BOTTOMRIGHT:
                return True, msg  # left edge is left-connected, move on

        msg = "Bottom-left edge of " + str(cand_hex) + " is not left-connected"
        return False, msg

    def _left_right_edge(self, cand_hex, border_val):
        msg = ''
        if border_val and Hex.BOTTOM:
            return True, msg  # left edge is right-connected, move on
        neighbour = Hex.get_neighbor(cand_hex, 4)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOMRIGHT:
                return True, msg  # left edge is right-connected, move on

        msg = "Bottom-left edge of " + str(cand_hex) + " is not right-connected"
        return False, msg

    def _right_left_edge(self, cand_hex, border_val):
        msg = ''
        if border_val and Hex.BOTTOM:
            return True, msg  # right edge is left-connected, move on

        neighbour = Hex.get_neighbor(cand_hex, 3)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOMLEFT:
                return True, msg  # right edge is left-connected, move on

        msg = "Bottom-right edge of " + str(cand_hex) + " is not left-connected"
        return False, msg

    def _right_right_edge(self, cand_hex, border_val):
        msg = ''
        neighbour = Hex.get_neighbor(cand_hex, 1)
        neighbour_val = self.borders.get(neighbour, False)
        if neighbour_val is not False:
            if neighbour_val & Hex.BOTTOM:
                return True, msg  # right edge is right-connected, move on
            if neighbour_val & Hex.BOTTOMLEFT:
                return True, msg  # right edge is right-connected, move on

        msg = "Bottom-right edge of " + str(cand_hex) + " is not right-connected"
        return False, msg

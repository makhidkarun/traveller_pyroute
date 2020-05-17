"""
Created on Mar 26, 2014

@author: tjoneslo
"""
import logging
from operator import itemgetter
from collections import defaultdict
import os


class AllyGen(object):
    """
    classdocs
    """
    noOne = ['--', '??', 'Xx']
    nonAligned = ['Na', 'Ns', 'Va', 'Cs', 'Hc',
                  'NaHv', 'NaDr', 'NaVa', 'NaAs', 'NaXx', 'NaXX', "NaSo",
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
                   ("Kk", "KkTw", "Kc", "KC"),
                   ('So', 'SoCf', 'SoBF', 'SoCT', 'SoFr', 'SoHn', 'SoKv', 'SoNS',
                    'SoQu', 'SoRD', 'SoRz', 'SoWu' ),
                   ('Lp', 'CoLp'),
                   ('Vd', 'VDeG'),
                   ('Vo', 'VOpA'),
                   ('Vx', 'VAsP'),
                   ('V9', 'VInL'),
                   ('Zh', 'ZhAx', 'ZhCa', 'ZhCh', 'ZhCo', 'ZhIa', 'ZhIN',
                    'ZhJp', 'ZhMe', 'ZhOb', 'ZhSh', 'ZhVQ')]

    default_population = {
        "As": "Asla",
        "Hv": "Hive",
        "JP": "Huma",
        "Kk": "KXKr",
        "Pd": "Piri",
        "Te": "Piri",
        "Tk": "Piri",
        "Va": "Varg",
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
        "MaEm": "Mask",
        "MaPr": "MalX",
        "NaAs": "Asla",
        "NaHv": "Hive",
        "NaVa": "Varg",
        "OcWs": "Stal",
        "SaCo": "Vlaz",
        "Sark": "Varg",
        "SwFW": "Swan",
        "VaEx": "Varg",
        "ZhAx": "Adda",
        "ZhCa": "Vlaz"
    }


    def __init__(self, galaxy):
        """
        Constructor
        """
        self.galaxy = galaxy
        self.borders = {}  # 2D array using (q,r) as key, with flags for data
        self.allyMap = {}
        self.logger = logging.getLogger('PyRoute.AllyGen')

    @staticmethod
    def is_unclaimed(alg):
        return alg in AllyGen.noOne

    @staticmethod
    def is_nonaligned(alg):
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
        # Try get the default cases
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
        # only what the base allegiances
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

    def create_borders(self, match):
        """
            Create borders around various allegiances, Algorithm one.
            From the nroute.c generation system. Every world controls a
            two hex radius. Where the allegiances are the same, the area
            of control is contiguous. Every Non-aligned world is independent
        """
        self.logger.info('Processing worlds for border drawing')
        for star in self.galaxy.stars:
            alg = star.alg_code
            # Skip the non-entity worlds
            if alg in self.noOne:
                continue
            # Collapse non-aligned into each their own 
            if alg in self.nonAligned:
                alg = self.nonAligned[0]
            # Collapse same Aligned into one
            alg = self.same_align(alg) if match == 'collapse' else alg

            self.allyMap[(star.q, star.r)] = alg

        # self._output_map(allyMap, 0)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 1)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 2)

        self._generate_borders(self.allyMap)

    def _generate_borders(self, allyMap):
        """
        Convert the allyMap, which is a dict of (q,r) keys with allegiance codes
        as values, into the borders, which is a dict of (q.r) keys with flags
        indicating which side of the Hex needs to have a border drawn on:
        1: top or bottom
        2: upper left or upper right
        4: lower left or lower right

        This is a bit of a mess because the line drawing in HexMap is a little strange,
        So the complexity is here to make the draw portion quick.
        """
        for Hex in list(allyMap.keys()):
            if self._set_border(allyMap, Hex, 2):  # up
                neighbor = AllyGen._get_neighbor(Hex, 2)
                self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 1
            if self._set_border(allyMap, Hex, 5):  # down
                self.borders[Hex] = self.borders.setdefault(Hex, 0) | 1
            if self._set_border(allyMap, Hex, 1):  # upper right
                neighbor = AllyGen._get_neighbor(Hex, 1)
                if Hex[0] & 1:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 2
                else:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 4
            if self._set_border(allyMap, Hex, 3):  # upper left
                if Hex[0] & 1:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 2
                else:
                    self.borders[(Hex[0], Hex[1] - 1)] = self.borders.setdefault((Hex[0], Hex[1] - 1), 0) | 4
            if self._set_border(allyMap, Hex, 0):  # down right
                neighbor = AllyGen._get_neighbor(Hex, 0)
                if Hex[0] & 1:
                    self.borders[(Hex[0] + 1, Hex[1] - 1)] = self.borders.setdefault((Hex[0] + 1, Hex[1] - 1), 0) | 4
                else:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 2
            if self._set_border(allyMap, Hex, 4):  # down left
                if Hex[0] & 1:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 4
                else:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 2

    @staticmethod
    def _set_border(allyMap, Hex, direction):
        """
        Determine if the allegiance is different in the direction,
        hence requiring adding a border to the map.
        returns True if border needed, False if not
        """
        neighbor = AllyGen._get_neighbor(Hex, direction)
        # if this is a non-aligned controlled hex, 
        # and the neighbor has no setting ,
        # or the neighbor is aligned 
        # Then no border . 
        if (allyMap[Hex] in AllyGen.nonAligned or allyMap[Hex] is None) and \
                (allyMap.get(neighbor, True) or allyMap.get(neighbor, None) not in AllyGen.nonAligned):
            return False
        # If not matched allegiance, need a border.
        elif allyMap[Hex] != allyMap.get(neighbor, None):
            return True
        return False

    @staticmethod
    def _get_neighbor(Hex, direction, distance=1):
        """
        determine neighboring hex from the q,r position and direction
        """
        neighbors = [
            [+1, 0], [+1, -1], [0, -1],
            [-1, 0], [-1, +1], [0, +1]
        ]
        d = neighbors[direction]
        qn = Hex[0] + (d[0] * distance)
        rn = Hex[1] + (d[1] * distance)
        return (int(qn), int(rn))

    @staticmethod
    def step_map(allyMap):
        newMap = {}
        for Hex in allyMap.keys():
            AllyGen._check_direction(allyMap, Hex, newMap)
        return newMap

    @staticmethod
    def _check_direction(allyMap, Hex, newMap):
        newMap[Hex] = allyMap[Hex]
        for direction in range(6):
            neighbor = AllyGen._get_neighbor(Hex, direction)
            if not allyMap.get(neighbor, False):
                newMap[neighbor] = allyMap[Hex]

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

    def create_ally_map(self, match):
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
        self._generate_borders(self.allyMap)

    def _ally_map(self, match):
        # Create list of stars
        stars = [star for star in self.galaxy.stars]
        allyMap = defaultdict(set)
        starMap = {}
        # Mark the map with all the stars        
        for star in stars:
            alg = star.alg_code
            # Collapse non-aligned into one value
            if alg in self.nonAligned or alg in self.noOne:
                alg = self.nonAligned[0]

            # Collapse same Aligned into one
            if match == 'collapse':
                alg = self.same_align(alg)
            elif match == 'separate':
                pass
            allyMap[(star.q, star.r)].add((alg, 0))
            starMap[(star.q, star.r)] = alg

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            # skip the E/X ports 
            Hex = (star.q, star.r)
            alg = starMap[Hex]

            if star.port in ['E', 'X']:
                maxRange = 1
            else:
                maxRange = ['D', 'C', 'B', 'A'].index(star.port) + 2
            if alg in self.nonAligned:
                maxRange = 2
            for dist in range(maxRange):
                neighbor = AllyGen._get_neighbor(Hex, 4, dist)
                for direction in range(6):
                    for _ in range(dist):
                        allyMap[neighbor].add((alg, star.axial_distance(Hex, neighbor)))
                        neighbor = AllyGen._get_neighbor(neighbor, direction)

        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 2: non-aligned worlds at dist 1 get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire. 
        for Hex in allyMap.keys():
            if len(allyMap[Hex]) == 1:
                allyMap[Hex] = allyMap[Hex].pop()[0]
            else:
                allyList = sorted([algs for algs in allyMap[Hex]], key=itemgetter(1))
                if allyList[0][1] == 0:
                    allyMap[Hex] = allyList[0][0]
                else:
                    minDistance = allyList[0][1]
                    allyDist = [algs for algs in allyList if algs[1] == minDistance]
                    if len(allyDist) == 1:
                        allyMap[Hex] = allyDist[0][0]
                    else:
                        maxCount = -1
                        maxAlly = None
                        for alg, dist in allyDist:
                            if alg in self.nonAligned:
                                maxAlly = alg
                                break
                            if self.galaxy.alg[alg].stats.number > maxCount:
                                maxAlly = alg
                                maxCount = self.galaxy.alg[alg].stats.number
                        allyMap[Hex] = maxAlly

        # self._output_map(allyMap, 2)

        # Pass 3: find lonely claimed hexes and remove them
        # Do two passes through the data
        for _ in range(2):
            for Hex in allyMap.keys():
                if starMap.get(Hex, False):
                    continue
                neighborAlgs = defaultdict(int)
                for direction in range(6):
                    neighborAlg = allyMap.get(AllyGen._get_neighbor(Hex, direction), None)
                    neighborAlgs[neighborAlg] += 1

                algList = sorted(iter(neighborAlgs.iteritems()), key=itemgetter(1), reverse=True)
                if len(algList) == 0:
                    allyMap[Hex] = None
                elif algList[0][1] >= 1:
                    allyMap[Hex] = algList[0][0]
                else:
                    allyMap[Hex] = self.nonAligned[0]
        return allyMap

    def create_erode_border(self, match):
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
        self._generate_borders(allyMap)

    def _erode(self, allyMap, starMap):
        """
        Remove edges.
        """
        newMap = {}
        changed = False

        # Erode, remove empty hex from polity 
        # if three contiguous hexes are not aligned
        for Hex in allyMap.keys():
            # Worlds keep their allegiances.
            if starMap.get(Hex, False):
                newMap[Hex] = starMap[Hex]
                continue
            if allyMap[Hex] in AllyGen.nonAligned or allyMap[Hex] in AllyGen.noOne:
                newMap[Hex] = allyMap[Hex]
                continue

            # Check for three continuous empty hexes around this hex
            for direction in range(6):
                notCount = 0
                for check in range(3):
                    checkHex = AllyGen._get_neighbor(Hex, (direction + check) % 6)
                    neighborAlg = allyMap.get(checkHex, None)
                    if not AllyGen.are_allies(allyMap[Hex], neighborAlg):
                        notCount += 1
                if notCount >= 3:
                    break

            if notCount >= 3:
                changed = True
            else:  # No empty hex range found, keep allegiance.
                newMap[Hex] = allyMap[Hex]
        return changed, newMap

    def _break_spans(self, allyMap, starMap):
        """'
        BreakSpans - Find a span of four empty (edge) hexes
        and break the span by setting one to not aligned.
        """
        edgeMap = {}
        changed = False
        # Create the edge map, of hexes on the border
        for Hex in allyMap.keys():
            for direction in range(6):
                checkHex = AllyGen._get_neighbor(Hex, direction)
                neighborAlg = allyMap.get(checkHex, None)
                if not AllyGen.are_allies(allyMap[Hex], neighborAlg):
                    edgeMap[Hex] = allyMap[Hex]

        for Hex in edgeMap.keys():
            if starMap.get(Hex, False):
                continue
            for direction in range(6):
                if self._check_aligned(starMap, edgeMap, Hex, direction, 1) and \
                        self._check_aligned(starMap, edgeMap, Hex, direction, 2) and \
                        self._check_aligned(starMap, edgeMap, Hex, direction, 3):
                    checkHex = AllyGen._get_neighbor(Hex, direction, 1)
                    allyMap[checkHex] = None
                    edgeMap[checkHex] = None
                    changed = True
                    break

        return changed, allyMap

    def _check_aligned(self, starMap, edgeMap, Hex, direction, distance):
        startAlleg = edgeMap[Hex]
        checkHex = AllyGen._get_neighbor(Hex, direction, distance)
        # Occupied hex does not count as aligned for this check
        if starMap.get(checkHex, False):
            return False
        checkAlleg = edgeMap.get(checkHex, None)
        return AllyGen.are_allies(startAlleg, checkAlleg)

    def _build_bridges(self, allyMap, starMap):
        """
        Build a bridge between two worlds one hex apart as to avoid
        disrupting contiguous empires.
        """
        for Hex in starMap.keys():
            self._search_range(Hex, allyMap, starMap)

    def _search_range(self, Hex, allyMap, starMap):
        from Star import Star
        newBridge = None
        checked = []
        for direction in range(6):
            checkHex = AllyGen._get_neighbor(Hex, direction)
            if starMap.get(checkHex, False):
                if self.are_allies(starMap[Hex], starMap[checkHex]):
                    checked.append(checkHex)
                continue
            if self.are_allies(starMap[Hex], allyMap.get(checkHex, None)):
                checked.append(checkHex)
                continue
            for second in range(6):
                searchHex = AllyGen._get_neighbor(checkHex, second)
                if searchHex in checked:
                    newBridge = None
                    continue
                if searchHex == Hex or Star.axial_distance(searchHex, Hex) == 1:
                    continue
                if starMap.get(searchHex, False) and \
                        self.are_allies(starMap[Hex], starMap[searchHex]):
                    newBridge = checkHex
                    checked.append(checkHex)
        if newBridge:
            allyMap[newBridge] = starMap[Hex]

    def _erode_map(self, match):
        """
        Generate the initial map of allegiances for the erode map.
        Note: This does not match the original system.
        """
        # Create list of stars
        stars = [star for star in self.galaxy.stars]
        allyMap = defaultdict(set)
        starMap = {}
        # Mark the map with all the stars        
        for star in stars:
            alg = star.alg_code
            # Collapse non-aligned into one value
            if alg in self.nonAligned or alg in self.noOne:
                alg = self.nonAligned[0]

            # Collapse same Aligned into one
            if match == 'collapse':
                alg = self.same_align(alg)
            elif match == 'separate':
                pass
            allyMap[(star.q, star.r)].add((alg, 0))
            starMap[(star.q, star.r)] = alg

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            Hex = (star.q, star.r)
            alg = starMap[Hex]

            if star.port in ['E', 'X', '?']:
                maxRange = 1
            else:
                maxRange = ['D', 'C', 'B', 'A'].index(star.port) + 2

            if alg in self.nonAligned:
                maxRange = 0
            # Walk the ring filling in the hexes around star with this neighbor
            for dist in range(1, maxRange):
                # Start in direction 0, at distance n
                neighbor = self._get_neighbor(Hex, 4, dist)
                # walk six sides
                for side in range(6):
                    for _ in range(dist):
                        allyMap[neighbor].add((alg, star.axial_distance(Hex, neighbor)))
                        neighbor = self._get_neighbor(neighbor, side)
        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire. 
        for Hex in allyMap.keys():
            if len(allyMap[Hex]) == 1:
                allyMap[Hex] = allyMap[Hex].pop()[0]
            else:
                allyList = sorted([algs for algs in allyMap[Hex]], key=itemgetter(1))
                if allyList[0][1] == 0:
                    allyMap[Hex] = allyList[0][0]
                else:
                    minDistance = allyList[0][1]
                    allyDist = [algs for algs in allyList if algs[1] == minDistance]
                    if len(allyDist) == 1:
                        allyMap[Hex] = allyDist[0][0]
                    else:
                        maxCount = -1
                        maxAlly = None
                        for alg, dist in allyDist:
                            if alg not in self.nonAligned and \
                                    self.galaxy.alg[alg].stats.number > maxCount:
                                maxAlly = alg
                                maxCount = self.galaxy.alg[alg].stats.number
                        allyMap[Hex] = maxAlly

        return allyMap, starMap

"""
Created on Oct 19, 2024

@author: CyberiaResurrection
"""
from collections import defaultdict
import logging
from operator import itemgetter
import os

from PyRoute.Allies.AllyGen import AllyGen
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.Position.Hex import Hex


class Borders(object):

    def __init__(self, galaxy: Galaxy):
        """
        Constructor
        """
        self.galaxy = galaxy
        self.borders = {}  # 2D array using (q,r) as key, with flags for data
        self.borders_map = {}  # 2D array using (q,r) as key, with flags for data, linking borders and hex-map
        self.allyMap = {}  # 2D array using (q,r) as key, with allegiance code as data
        self.logger = logging.getLogger('PyRoute.Borders')

    def create_borders(self, match: str, enforce=True):
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
                alg = AllyGen.nonAligned[0]
            # Collapse same Aligned into one
            alg = self._collapse_allegiance_if_needed(alg, match)

            self.allyMap[(star.q, star.r)] = alg

        # self._output_map(allyMap, 0)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 1)

        self.allyMap = self.step_map(self.allyMap)
        # self._output_map(allyMap, 2)

        self._generate_borders(self.allyMap, enforce)

    def _generate_borders(self, allyMap: dict, enforce=True):
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
    def _set_border(allyMap: dict, cand_hex: tuple[int, int], direction: int):
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
    def step_map(allyMap: dict):
        newMap = {}
        for cand_hex in allyMap.keys():
            Borders._check_direction(allyMap, cand_hex, newMap)
        return newMap

    @staticmethod
    def _check_direction(allyMap: dict, cand_hex: tuple[int, int], newMap: dict):
        newMap[cand_hex] = allyMap[cand_hex]
        for direction in range(6):
            neighbor = Hex.get_neighbor(cand_hex, direction)
            if neighbor not in allyMap:
                newMap[neighbor] = allyMap[cand_hex]

    def _output_map(self, allyMap: dict, stage: int):
        path = os.path.join(self.galaxy.output_path, 'allyMap%s.txt' % stage)
        with open(path, "wb") as f:
            for key, value in allyMap.items():
                f.write("{}-{}: border: {}\n".format(key[0], key[1], value))

    def create_ally_map(self, match: str, enforce=True):
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

    def _ally_map(self, match: str):
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
                    allyMap[cand_hex] = AllyGen.nonAligned[0]

        return allyMap

    def create_erode_border(self, match: str, enforce=True):
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

    def _erode(self, allyMap: dict, starMap: dict):
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

    def _break_spans(self, allyMap: dict, starMap: dict):
        """'
        BreakSpans - Find a span of four empty (edge) hexes
        and break the span by setting one to not aligned.
        """
        edgeMap = {}
        changed = False
        # Create the edge map, of hexes on the border
        for cand_hex in allyMap.keys():
            cand_ally = allyMap[cand_hex]
            for direction in range(6):
                checkHex = Hex.get_neighbor(cand_hex, direction)
                if not AllyGen.are_allies(cand_ally, allyMap.get(checkHex, None)) and cand_hex not in starMap:
                    edgeMap[cand_hex] = cand_ally

        for cand_hex in edgeMap.keys():
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

    def _check_aligned(self, starMap: dict, edgeMap: dict, cand_hex: tuple[int, int], direction: int, distance: int):
        startAlleg = edgeMap[cand_hex]
        checkHex = Hex.get_neighbor(cand_hex, direction, distance)
        # Occupied hex does not count as aligned for this check
        if checkHex in starMap:
            return False
        checkAlleg = edgeMap.get(checkHex, None)
        return AllyGen.are_allies(startAlleg, checkAlleg)

    def _build_bridges(self, allyMap: dict, starMap: dict):
        """
        Build a bridge between two worlds one hex apart as to avoid
        disrupting contiguous empires.
        """
        for cand_hex in starMap.keys():
            self._search_range(cand_hex, allyMap, starMap)

    def _search_range(self, cand_hex: tuple[int, int], allyMap: dict, starMap: dict):
        newBridge = None
        checked = []
        star_candidate = starMap[cand_hex]
        neighbours = {}
        for direction in range(6):
            neighbours[direction] = Hex.get_neighbor(cand_hex, direction)

        for direction in range(6):
            checkHex = neighbours[direction]
            if checkHex in starMap:
                if AllyGen.are_allies(star_candidate, starMap[checkHex]):
                    checked.append(checkHex)
                continue
            if AllyGen.are_allies(star_candidate, allyMap.get(checkHex, None)):
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
                        AllyGen.are_allies(star_candidate, starMap[searchHex]):
                    newBridge = checkHex
                    checked.append(checkHex)
        if newBridge:
            allyMap[newBridge] = star_candidate

    def _erode_map(self, match: str):
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

    def _unpack_stars_and_maps(self, match: str):
        stars = self.galaxy.star_mapping.values()
        allyMap = defaultdict(set)
        starMap = {}
        # Mark the map with all the stars
        for star in stars:
            alg = star.alg_code
            # Collapse non-aligned into one value
            if AllyGen.is_nonaligned(alg):
                alg = AllyGen.nonAligned[0]

            # Collapse same Aligned into one
            alg = self._collapse_allegiance_if_needed(alg, match)

            allyMap[(star.q, star.r)].add((alg, 0))
            starMap[(star.q, star.r)] = alg
        return allyMap, starMap, stars

    def _collapse_allegiance_if_needed(self, alg: str, match: str):
        if 'collapse' == match:
            alg = AllyGen.same_align(alg)
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

    def _bottom_left_edge(self, cand_hex: tuple[int, int], border_val: int):
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

    def _bottom_right_edge(self, cand_hex: tuple[int, int], border_val: int):
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

    def _left_left_edge(self, cand_hex: tuple[int, int], border_val: int):
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

    def _left_right_edge(self, cand_hex: tuple[int, int], border_val: int):
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

    def _right_left_edge(self, cand_hex: tuple[int, int], border_val: int):
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

    def _right_right_edge(self, cand_hex: tuple[int, int], border_val: int):
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

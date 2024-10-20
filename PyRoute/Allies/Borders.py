"""
Created on Oct 19, 2024

@author: CyberiaResurrection
"""
from collections import defaultdict
import logging
from operator import itemgetter
import os

from PyRoute.Allies.AllyGen import AllyGen
import PyRoute.AreaItems.Galaxy as Galaxy
from PyRoute.Position.Hex import Hex
from PyRoute.Star import Star


class Borders(object):

    def __init__(self, galaxy: Galaxy):
        """
        Constructor
        """
        self.galaxy: Galaxy = galaxy
        self.borders: dict[tuple[int, int], int] = {}  # 2D array using (q,r) as key, with flags for data
        self.borders_map: dict[tuple[int, int], int] = {}  # 2D array using (q,r) as key, with flags for data, linking borders and hex-map
        self.allyMap: dict[tuple[int, int], str] = {}  # 2D array using (q,r) as key, with allegiance code as data
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

    def _generate_borders(self, ally_map: dict[tuple[int, int], str], enforce=True):
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
        for cand_hex in list(ally_map.keys()):
            odd_q = cand_hex[0] & 1
            if self._set_border(ally_map, cand_hex, 2):  # up
                neighbor = Hex.get_neighbor(cand_hex, 2)
                self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | Hex.BOTTOM
                self.borders_map[neighbor] = self.borders_map.setdefault(neighbor, 0) | Hex.BOTTOM
            if self._set_border(ally_map, cand_hex, 5):  # down
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOM
                self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOM
            if self._set_border(ally_map, cand_hex, 1):  # upper right
                neighbour = Hex.get_neighbor(cand_hex, 1)
                self.borders[neighbour] = self.borders.setdefault(neighbour, 0) | Hex.BOTTOMLEFT

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
            if self._set_border(ally_map, cand_hex, 3):  # upper left
                neighbour = Hex.get_neighbor(cand_hex, 3)
                self.borders[neighbour] = self.borders.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                neighbour = cand_hex if odd_q else Hex.get_neighbor(cand_hex, 2)

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
            if self._set_border(ally_map, cand_hex, 0):  # down right
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOMRIGHT
                neighbour = Hex.get_neighbor(cand_hex, 1) if odd_q else Hex.get_neighbor(cand_hex, 0)

                if odd_q:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMLEFT
                else:
                    self.borders_map[neighbour] = self.borders_map.setdefault(neighbour, 0) | Hex.BOTTOMRIGHT
            if self._set_border(ally_map, cand_hex, 4):  # down left
                self.borders[cand_hex] = self.borders.setdefault(cand_hex, 0) | Hex.BOTTOMLEFT

                if odd_q:
                    self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOMLEFT
                else:
                    self.borders_map[cand_hex] = self.borders_map.setdefault(cand_hex, 0) | Hex.BOTTOMRIGHT

        if enforce:
            result, msg = self.is_well_formed()
            assert result, msg

    @staticmethod
    def _set_border(ally_map: dict[tuple[int, int], str], cand_hex: tuple[int, int], direction: int) -> bool:
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
        cand_hex_not_aligned = (AllyGen.is_nonaligned(ally_map[cand_hex], True) or ally_map[cand_hex] is None)
        neighbour_is_aligned = (ally_map.get(neighbor, True) or ally_map.get(neighbor, None) not in AllyGen.nonAligned)
        if cand_hex_not_aligned and neighbour_is_aligned:
            return False
        # If not matched allegiance, need a border.
        elif ally_map[cand_hex] != ally_map.get(neighbor, None):
            return True
        return False

    @staticmethod
    def step_map(ally_map: dict[tuple[int, int], str]) -> dict[tuple[int, int], str]:
        new_map = {}
        for cand_hex in ally_map.keys():
            Borders._check_direction(ally_map, cand_hex, new_map)
        return new_map

    @staticmethod
    def _check_direction(ally_map: dict[tuple[int, int], str], cand_hex: tuple[int, int], new_map: dict[tuple[int, int], str]):
        new_map[cand_hex] = ally_map[cand_hex]
        for direction in range(6):
            neighbor = Hex.get_neighbor(cand_hex, direction)
            if neighbor not in ally_map:
                new_map[neighbor] = ally_map[cand_hex]

    def _output_map(self, ally_map: dict[tuple[int, int], str], stage: int):
        path = os.path.join(self.galaxy.output_path, 'allyMap%s.txt' % stage)
        with open(path, "wb") as f:
            for key, value in ally_map.items():
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

    def _ally_map(self, match: str) -> dict[tuple[int, int], str]:
        # Create list of stars
        ally_map, star_map, stars = self._unpack_stars_and_maps(match)

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            # skip the E/X ports
            cand_hex = (star.q, star.r)
            alg = star_map[cand_hex]

            if star.port in ['E', 'X']:
                max_range = 1
            else:
                max_range = ['D', 'C', 'B', 'A'].index(star.port) + 2
            if AllyGen.is_nonaligned(alg, True):
                max_range = 2
            for dist in range(max_range):
                neighbor = Hex.get_neighbor(cand_hex, 4, dist)
                for direction in range(6):
                    for _ in range(dist):
                        star_dist = Hex.axial_distance(cand_hex, neighbor)
                        ally_map[neighbor].add((alg, star_dist))
                        neighbor = Hex.get_neighbor(neighbor, direction)

        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 2: non-aligned worlds at dist 1 get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire.
        for cand_hex in ally_map.keys():
            if len(ally_map[cand_hex]) == 1:
                ally_map[cand_hex] = ally_map[cand_hex].pop()[0]
            else:
                ally_list = sorted([algs for algs in ally_map[cand_hex]], key=itemgetter(1))
                if ally_list[0][1] == 0:
                    ally_map[cand_hex] = ally_list[0][0]
                else:
                    min_distance = ally_list[0][1]
                    ally_dist = [algs for algs in ally_list if algs[1] == min_distance]
                    if len(ally_dist) == 1:
                        ally_map[cand_hex] = ally_dist[0][0]
                    else:
                        max_count = -1
                        max_ally = None
                        for alg, dist in ally_dist:
                            if AllyGen.is_nonaligned(alg, True):
                                max_ally = alg
                                break
                            if self.galaxy.alg[alg].stats.number > max_count:
                                max_ally = alg
                                max_count = self.galaxy.alg[alg].stats.number
                        ally_map[cand_hex] = max_ally

        # self._output_map(allyMap, 2)

        # Pass 3: find lonely claimed hexes and remove them
        # Do two passes through the data
        for _ in range(2):
            for cand_hex in ally_map.keys():
                if cand_hex in star_map:
                    continue
                neighbor_algs = defaultdict(int)
                for direction in range(6):
                    neighbor_alg = ally_map.get(Hex.get_neighbor(cand_hex, direction), None)
                    neighbor_algs[neighbor_alg] += 1

                alg_list = sorted(iter(neighbor_algs.items()), key=itemgetter(1), reverse=True)
                if len(alg_list) == 0:
                    ally_map[cand_hex] = None
                elif alg_list[0][1] >= 1:
                    ally_map[cand_hex] = alg_list[0][0]
                else:
                    ally_map[cand_hex] = AllyGen.nonAligned[0]

        return ally_map

    def create_erode_border(self, match: str, enforce=True):
        """
        Create borders around various allegiances, Algorithm Three.
        From TravellerMap http://travellermap.com/borders/doc.htm
        """
        self.logger.info('Processing worlds for erode map drawing')
        ally_map, star_map = self._erode_map(match)
        changed = True
        change_count = 0
        while changed:
            if change_count == 100:
                self.logger.error('Change count for map processing exceeded expected value of 100')
                break
            changed, ally_map = self._erode(ally_map, star_map)
            if not changed:
                changed, ally_map = self._break_spans(ally_map, star_map)
            change_count += 1

        self.logger.debug('Change Count: {}'.format(change_count))
        self._build_bridges(ally_map, star_map)

        self.allyMap = ally_map
        self._generate_borders(ally_map, enforce)

    def _erode(self, ally_map: dict[tuple[int, int], str], star_map: dict[tuple[int, int], str]) -> (bool, dict[tuple[int, int], str]):
        """
        Remove edges.
        """
        new_map = {}
        changed = False

        # Erode, remove empty hex from polity
        # if three contiguous hexes are not aligned

        for cand_hex in ally_map.keys():
            # Worlds keep their allegiances.
            if cand_hex in star_map:
                new_map[cand_hex] = star_map[cand_hex]
                continue

            ally_map_candidate = ally_map[cand_hex]

            # The direction/check combo hits all 6 surrounding hexen up 3 times apiece, and, per profiling, is
            # the heaviest chunk of runtime in the whole method (previously 80%+ of runtime), so it's worth
            # memoising.
            not_ally_neighbours = dict()

            # Check for three continuous empty hexes around this cand_hex
            for direction in range(6):
                # pre-heat not_ally_neighbours
                check_hex = Hex.get_neighbor(cand_hex, direction)
                not_ally_neighbours[direction] = not AllyGen.are_allies(ally_map_candidate, ally_map.get(check_hex, None))

            # Only spin through neighbours if there's 3 or more empty hexen - doing this with 2 or fewer empty
            # hexen is a hiding to nowhere, as 3 continuous empty hexen _can't_ exist
            not_count = 0
            if 2 < sum(not_ally_neighbours.values()):
                for direction in range(6):
                    not_count = 0
                    for check in range(3):
                        if not_ally_neighbours[(direction + check) % 6]:
                            not_count += 1
                    if not_count >= 3:
                        break

            if not_count >= 3:
                changed = True
            else:  # No empty hex in range found, keep allegiance.
                new_map[cand_hex] = ally_map_candidate
        return changed, new_map

    def _break_spans(self, ally_map: dict[tuple[int, int], str], star_map: dict[tuple[int, int], str]) -> (bool, dict[tuple[int, int], str]):
        """'
        BreakSpans - Find a span of four empty (edge) hexes
        and break the span by setting one to not aligned.
        """
        edge_map = {}
        changed = False
        # Create the edge map, of hexes on the border
        for cand_hex in ally_map.keys():
            cand_ally = ally_map[cand_hex]
            for direction in range(6):
                check_hex = Hex.get_neighbor(cand_hex, direction)
                if not AllyGen.are_allies(cand_ally, ally_map.get(check_hex, None)) and cand_hex not in star_map:
                    edge_map[cand_hex] = cand_ally

        for cand_hex in edge_map.keys():
            for direction in range(6):
                if self._check_aligned(star_map, edge_map, cand_hex, direction, 1) and \
                        self._check_aligned(star_map, edge_map, cand_hex, direction, 2) and \
                        self._check_aligned(star_map, edge_map, cand_hex, direction, 3):
                    check_hex = Hex.get_neighbor(cand_hex, direction, 1)
                    ally_map[check_hex] = None
                    edge_map[check_hex] = None
                    changed = True
                    break

        return changed, ally_map

    def _check_aligned(self, star_map: dict[tuple[int, int], str], edge_map: dict[tuple[int, int], str], cand_hex: tuple[int, int], direction: int, distance: int) -> bool:
        start_alleg = edge_map[cand_hex]
        check_hex = Hex.get_neighbor(cand_hex, direction, distance)
        # Occupied hex does not count as aligned for this check
        if check_hex in star_map:
            return False
        check_alleg = edge_map.get(check_hex, None)
        return AllyGen.are_allies(start_alleg, check_alleg)

    def _build_bridges(self, ally_map: dict[tuple[int, int], str], star_map: dict[tuple[int, int], str]):
        """
        Build a bridge between two worlds one hex apart as to avoid
        disrupting contiguous empires.
        """
        for cand_hex in star_map.keys():
            self._search_range(cand_hex, ally_map, star_map)

    def _search_range(self, cand_hex: tuple[int, int], ally_map: dict[tuple[int, int], str], star_map: dict[tuple[int, int], str]):
        new_bridge = None
        checked = []
        star_candidate = star_map[cand_hex]
        neighbours = {}
        for direction in range(6):
            neighbours[direction] = Hex.get_neighbor(cand_hex, direction)

        for direction in range(6):
            check_hex = neighbours[direction]
            if check_hex in star_map:
                if AllyGen.are_allies(star_candidate, star_map[check_hex]):
                    checked.append(check_hex)
                continue
            if AllyGen.are_allies(star_candidate, ally_map.get(check_hex, None)):
                checked.append(check_hex)
                continue
            for second in range(6):
                search_hex = Hex.get_neighbor(check_hex, second)
                if search_hex in checked:
                    new_bridge = None
                    continue
                if search_hex == cand_hex or Hex.axial_distance(search_hex, cand_hex) == 1:
                    continue
                if search_hex in star_map and \
                        AllyGen.are_allies(star_candidate, star_map[search_hex]):
                    new_bridge = check_hex
                    checked.append(check_hex)
        if new_bridge:
            ally_map[new_bridge] = star_candidate

    def _erode_map(self, match: str) -> (dict[tuple[int, int], str], dict[tuple[int, int], str]):
        """
        Generate the initial map of allegiances for the erode map.
        Note: This does not match the original system.
        """
        # Create list of stars
        ally_map, star_map, stars = self._unpack_stars_and_maps(match)

        # self._output_map(allyMap, 0)

        # Pass 1: generate initial allegiance arrays,
        # with overlapping maps
        for star in stars:
            cand_hex = (star.q, star.r)
            alg = star_map[cand_hex]

            if AllyGen.is_nonaligned(alg, True):
                max_range = 0
            elif star.port in ['E', 'X', '?']:
                max_range = 1
            else:
                max_range = ['D', 'C', 'B', 'A'].index(star.port) + 2

            # Walk the ring filling in the hexes around star with this neighbor
            for dist in range(1, max_range):
                # Start in direction 0, at distance n
                neighbor = Hex.get_neighbor(cand_hex, 4, dist)
                # walk six sides
                for side in range(6):
                    for _ in range(dist):
                        ally_map[neighbor].add((alg, Hex.axial_distance(cand_hex, neighbor)))
                        neighbor = Hex.get_neighbor(neighbor, side)
        # self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 0: hexes with only one claimant, give it to them
        # 1: hexes with the world (dist 0) get selected
        # 3: hexes claimed by two (or more) allies are pushed to the closest world
        # 4: hexes claimed by two (or more) allies at the same distance
        #    are claimed by the larger empire.
        for cand_hex in ally_map.keys():
            if len(ally_map[cand_hex]) == 1:
                ally_map[cand_hex] = ally_map[cand_hex].pop()[0]
            else:
                ally_list = sorted([algs for algs in ally_map[cand_hex]], key=itemgetter(1))
                if ally_list[0][1] == 0:
                    ally_map[cand_hex] = ally_list[0][0]
                else:
                    min_distance = ally_list[0][1]
                    ally_dist = [algs for algs in ally_list if algs[1] == min_distance]
                    if len(ally_dist) == 1:
                        ally_map[cand_hex] = ally_dist[0][0]
                    else:
                        max_count = -1
                        max_ally = None
                        for alg, dist in ally_dist:
                            if not AllyGen.is_nonaligned(alg, True) and \
                                    self.galaxy.alg[alg].stats.number > max_count:
                                max_ally = alg
                                max_count = self.galaxy.alg[alg].stats.number
                        ally_map[cand_hex] = max_ally

        return ally_map, star_map

    def _unpack_stars_and_maps(self, match: str) -> (dict[tuple[int, int], str], dict[tuple[int, int], str], list[Star]):
        stars = self.galaxy.star_mapping.values()
        ally_map = defaultdict(set)
        star_map = {}
        # Mark the map with all the stars
        for star in stars:
            alg = star.alg_code
            # Collapse non-aligned into one value
            if AllyGen.is_nonaligned(alg):
                alg = AllyGen.nonAligned[0]

            # Collapse same Aligned into one
            alg = self._collapse_allegiance_if_needed(alg, match)

            ally_map[(star.q, star.r)].add((alg, 0))
            star_map[(star.q, star.r)] = alg
        return ally_map, star_map, stars

    def _collapse_allegiance_if_needed(self, alg: str, match: str) -> str:
        if 'collapse' == match:
            alg = AllyGen.same_align(alg)
        elif 'separate' == match:
            pass
        return alg

    def is_well_formed(self) -> (bool, str):
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

    def _bottom_left_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

    def _bottom_right_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

    def _left_left_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

    def _left_right_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

    def _right_left_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

    def _right_right_edge(self, cand_hex: tuple[int, int], border_val: int) -> (bool, str):
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

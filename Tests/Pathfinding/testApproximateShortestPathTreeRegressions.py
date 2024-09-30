import argparse
import os
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
from Tests.baseTest import baseTest


class testApproximateShortestPathTreeRegressions(baseTest):
    def test_restart_blowup(self):
        sourcefile = self.unpack_filename('DeltaFiles/dijkstra_restart_blowup/Lishun.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_restart_blowup_on_jump_4(self):
        sourcefile = self.unpack_filename('DeltaFiles/dijkstra_restart_blowup/Lishun-jump4.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_restart_blowup_on_jump_4_1(self):
        sourcefile = self.unpack_filename('DeltaFiles/dijkstra_restart_blowup/Lishun-jump4-1.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_stars_node_types(self):
        sourcefile = self.unpack_filename('DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.process_owned_worlds()

    def test_stars_node_types_comm(self):
        sourcefile = self.unpack_filename('DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'comm'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_comm_dont_change_iterator_in_flight(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'comm'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_node_types_xroute(self):
        sourcefile = self.unpack_filename('DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'xroute'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_node_types_xroute_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/xroute_calculation_blowups/Antares-Urunishu.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'xroute'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_node_types_xroute_two_subsectors(self):
        sourcefile = self.unpack_filename('DeltaFiles/xroute_calculation_blowups/Antares-Sakhag-Celebes.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'xroute'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_node_types_owned(self):
        sourcefile = self.unpack_filename('DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'owned'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.process_owned_worlds()

    def test_stars_node_types_none(self):
        sourcefile = self.unpack_filename('DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'none'

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars.nodes[item]['star'] for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(stars[0].index, galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.process_owned_worlds()

    def _make_args(self):
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = None
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = tempfile.gettempdir()
        args.debug_flag = False
        args.mp_threads = 1
        return args


if __name__ == '__main__':
    unittest.main()

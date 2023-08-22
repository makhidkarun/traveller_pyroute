import argparse
import os
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree


class testApproximateShortestPathTreeRegressions(unittest.TestCase):
    def test_restart_blowup(self):
        sourcefile = os.path.abspath('../DeltaFiles/dijkstra_restart_blowup/Lishun.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/dijkstra_restart_blowup/Lishun.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars_shadow.nodes[item]['star'] for item in galaxy.stars_shadow]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0].index, galaxy.stars_shadow, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_restart_blowup_on_jump_4(self):
        sourcefile = os.path.abspath('../DeltaFiles/dijkstra_restart_blowup/Lishun-jump4.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/dijkstra_restart_blowup/Lishun-jump4.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars_shadow.nodes[item]['star'] for item in galaxy.stars_shadow]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0].index, galaxy.stars_shadow, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_restart_blowup_on_jump_4_1(self):
        sourcefile = os.path.abspath('../DeltaFiles/dijkstra_restart_blowup/Lishun-jump4-1.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/dijkstra_restart_blowup/Lishun-jump4-1.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars_shadow.nodes[item]['star'] for item in galaxy.stars_shadow]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0].index, galaxy.stars_shadow, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

    def test_stars_node_types(self):
        sourcefile = os.path.abspath('../DeltaFiles/stars_node_types/Antares.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmark - biggest WTN system in the biggest graph component
        stars = [galaxy.stars_shadow.nodes[item]['star'] for item in galaxy.stars_shadow]
        stars.sort(key=lambda item: item.wtn, reverse=True)

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0].index, galaxy.stars_shadow, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.process_owned_worlds()

    def test_stars_node_types_comm(self):
        sourcefile = os.path.abspath('../DeltaFiles/stars_node_types/Antares.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/stars_node_types/Antares.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'comm'

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

        galaxy.process_owned_worlds()

    def test_stars_comm_dont_change_iterator_in_flight(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4
        args.routes = 'comm'

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.is_well_formed()
        galaxy.trade.calculate_routes()

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
        return args


if __name__ == '__main__':
    unittest.main()

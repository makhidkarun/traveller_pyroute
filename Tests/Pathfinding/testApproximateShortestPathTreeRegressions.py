import argparse
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from PyRoute.Pathfinding.astar import astar_path
from PyRoute.Pathfinding.single_source_dijkstra import single_source_dijkstra, implicit_shortest_path_dijkstra


class testApproximateShortestPathTreeRegressions(unittest.TestCase):
    def test_restart_blowup(self):
        sourcefile = '../DeltaFiles/dijkstra_restart_blowup/Lishun.sec'

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
        stars = [item for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        testrun = btn[7]
        btn = btn[0:7]


        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0], galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        star = testrun[0]
        neighbour = testrun[1]

        route = astar_path(galaxy.stars, star, neighbour, galaxy.heuristic_distance)

        galaxy.route_no_revisit(route)

        # manually land the route updates
        edges = list(zip(route[0:-1], route[1:]))

        for item in edges:
            galaxy.stars[item[0]][item[1]]['weight'] *= 0.9

        dropnodes = [route[0], route[2]]

        distances, paths, parent, kids, frontier = galaxy.trade.shortest_path_tree.drop_nodes(dropnodes)
        self.assertEqual(5, len(frontier))

        # Check no non-frontier nodes have frontier parents
        for node in distances.keys():
            if node not in frontier and parent[node] is not None:
                self.assertFalse(
                    parent[node] in frontier,
                    "Non-frontier node " + str(node) + " has frontier parent " + str(parent[node])
                )

        single_source_dijkstra(galaxy.stars, stars[0], distances=distances, frontier=frontier, paths=paths)

    def test_restart_blowup_on_jump_4(self):
        sourcefile = '../DeltaFiles/dijkstra_restart_blowup/Lishun-jump4.sec'

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
        stars = [item for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        testrun = btn[65]
        btn = btn[0:65]

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0], galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.trade.shortest_path_tree.is_well_formed()
        star = testrun[0]
        neighbour = testrun[1]

        route = astar_path(galaxy.stars, star, neighbour, galaxy.heuristic_distance)

        galaxy.route_no_revisit(route)

        # manually land the route updates
        edges = list(zip(route[0:-1], route[1:]))

        for item in edges:
            galaxy.stars[item[0]][item[1]]['weight'] *= 0.9

        # galaxy.trade.shortest_path_tree.update_edges(edges)

        dropnodes = [route[0]]

        distances, paths, parent, kids, frontier = galaxy.trade.shortest_path_tree.drop_nodes(dropnodes)

        # Check no non-frontier nodes have frontier parents
        for node in distances.keys():
            if node not in frontier and parent[node] is not None:
                self.assertFalse(
                    parent[node] in frontier,
                    "Non-frontier node " + str(node) + " has frontier parent " + str(parent[node])
                )

        single_source_dijkstra(galaxy.stars, stars[0], distances=distances, frontier=frontier, paths=paths)

    def test_restart_blowup_on_jump_4_1(self):
        sourcefile = '../DeltaFiles/dijkstra_restart_blowup/Lishun-jump4-1.sec'

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
        stars = [item for item in galaxy.stars]
        stars.sort(key=lambda item: item.wtn, reverse=True)
        stars[0].is_landmark = True

        testrun = btn[25]
        btn = btn[0:25]

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(stars[0], galaxy.stars, 0)
        for (star, neighbour, data) in btn:
            galaxy.trade.get_trade_between(star, neighbour)

        galaxy.trade.shortest_path_tree.is_well_formed()
        star = testrun[0]
        neighbour = testrun[1]

        route = astar_path(galaxy.stars, star, neighbour, galaxy.heuristic_distance)

        galaxy.route_no_revisit(route)

        # manually land the route updates
        edges = list(zip(route[0:-1], route[1:]))

        for item in edges:
            galaxy.stars[item[0]][item[1]]['weight'] *= 0.9

        galaxy.trade.shortest_path_tree.update_edges(edges)


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

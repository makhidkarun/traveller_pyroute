import unittest
import numpy as np

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest
try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified  # type: ignore
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified  # type: ignore
except AttributeError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified  # type: ignore


class testDeltaGalaxy(baseTest):
    def test_read_sectors(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-spiked.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)

        with self.assertRaises(Exception) as context:
            galaxy.read_sectors(delta, 'scaled', 'scaled',
                                10, 'trade', 8, 1, False)

        self.assertTrue('duplicated in sector Dagudashaag' in str(context.exception))

    def test_route_cost(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 15, 1, False)

        galaxy.generate_routes()
        star1 = galaxy.stars.nodes[0]['star']
        star2 = galaxy.stars.nodes[5]['star']
        star3 = galaxy.stars.nodes[6]['star']
        route = [star1, star2, star3]

        expected = 126
        actual = galaxy.route_cost(route)
        self.assertEqual(expected, actual, "Unexpected route cost")

    def test_route_no_revisit_true(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 15, 1, False)

        galaxy.generate_routes()
        star1 = galaxy.stars.nodes[0]['star']
        star2 = galaxy.stars.nodes[5]['star']
        star3 = galaxy.stars.nodes[6]['star']
        route = [star1, star2, star3]

        self.assertTrue(galaxy.route_no_revisit(route), "Unique route shouldn't revisit any star")

    def test_route_no_revisit_false(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 15, 1, False)

        galaxy.generate_routes()
        star1 = galaxy.stars.nodes[0]['star']
        star2 = galaxy.stars.nodes[5]['star']
        star3 = galaxy.stars.nodes[6]['star']
        route = [star1, star2, star3, star1]

        self.assertFalse(galaxy.route_no_revisit(route), "Non-unique route should revisit at least 1 star")

    def test_heuristic_distance_bulk(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 15, 1, False)

        galaxy.generate_routes()
        galaxy.trade.calculate_components()
        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars,
                                                                   galaxy.trade.epsilon)

        actual = galaxy.heuristic_distance_bulk(0)
        self.assertTrue(isinstance(actual, np.ndarray), "Actual not an ndarray")
        raw_expected = [0.00000, 132.72728, 134.54546, 134.54546, 111.81819, 47.27274, 109.09092, 132.72728,
                        69.09091, 110.90910, 132.72728, 155.45456, 155.45456, 132.72728, 90.90910, 133.63637,
                        131.81819, 174.54547, 196.36365, 19.09091, 42.72728, 84.54546, 173.63637, 133.63637,
                        132.72728, 106.36365, 158.18183, 24.54546, 89.09092, 83.63637, 45.45454, 28.18182,
                        50.90910, 69.09092, 91.81819, 85.45455, 117.27274]
        expected = np.array(raw_expected, dtype=float)
        self.assertEqual(len(expected), len(actual))
        delta = np.abs(expected - actual)
        self.assertTrue((delta < 0.00001).all(), "Unexpected bulk heuristic value")


if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy


class testDeltaGalaxy(unittest.TestCase):
    def test_read_sectors(self):
        sourcefile = 'DeltaFiles/Dagudashaag-spiked.sec'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4, 8)
        galaxy.read_sectors(delta, 'scaled', 'scaled')

        self.assertEqual(1, len(galaxy.sectors), "Galaxy should have one sector after load")
        self.assertEqual(
            'Dagudashaag',
            galaxy.sectors['Dagudashaag'].name,
            "Dagudashaag sector should be present after load"
        )
        self.assertEqual(
            561,
            len(galaxy.sectors['Dagudashaag'].worlds),
            "Unexpected world count in Dagudashaag sector after load"
        )
        # looks like the nx.Graph object deduplicates on addition, thus the duplicate system
        # not showing up in the overall count
        self.assertEqual(560, len(galaxy.stars), "Unexpected total world count after load")

    def test_verify_shared_shadow_mapping(self):
        sourcefile = 'DeltaFiles/Zarushagar-Ibara.sec'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4, 8)
        galaxy.read_sectors(delta, 'scaled', 'scaled')

        galaxy.generate_routes('trade', 10)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        shadow = galaxy.stars_shadow

        stars = list(graph.nodes)
        source = stars[0]
        adj_keys = graph[source].keys()
        target = list(adj_keys)[0]

        # first, verify _initial_ value
        initval = graph[source][target]['weight']
        shadowval = shadow[source.index][target.index]['weight']
        self.assertEqual(initval, shadowval, "Stars edge value between " + str(source) + " and " + str(target) + " not retrieved from stars_shadow")
        backshadowval = shadow[target.index][source.index]['weight']
        self.assertEqual(initval, backshadowval, "Stars edge value between " + str(source) + " and " + str(target) + " not retrieved from stars_shadow in reverse")

        # now verify value in reverse
        rev_val = graph[target][source]['weight']
        shadowval = shadow[source.index][target.index]['weight']
        self.assertEqual(rev_val, shadowval, "Stars edge value between " + str(target) + " and " + str(source) + " not retrieved from stars_shadow")
        backshadowval = shadow[target.index][source.index]['weight']
        self.assertEqual(rev_val, backshadowval, "Stars edge value between " + str(target) + " and " + str(source) + " not retrieved from stars_shadow in reverse")

        # initial values are verified, now to check they _propagated_
        graph[source][target]['weight'] -= 1
        shadowval = shadow[source.index][target.index]['weight']
        self.assertEqual(initval - 1, shadowval, "Propagated stars edge value between " + str(source) + " and " + str(
            target) + " not retrieved from stars_shadow")
        graph[source][target]['weight'] -= 1
        backshadowval = shadow[target.index][source.index]['weight']
        self.assertEqual(initval - 2, backshadowval, "Propagated stars edge value between " + str(source) + " and " + str(
            target) + " not retrieved from stars_shadow in reverse")
        graph[target][source]['weight'] -= 1
        shadowval = shadow[source.index][target.index]['weight']
        self.assertEqual(initval - 3, shadowval, "Stars edge value between " + str(target) + " and " + str(source) + " not retrieved from stars_shadow")
        graph[target][source]['weight'] -= 1
        backshadowval = shadow[target.index][source.index]['weight']
        self.assertEqual(initval - 4, backshadowval, "Stars edge value between " + str(target) + " and " + str(source) + " not retrieved from stars_shadow in reverse")


if __name__ == '__main__':
    unittest.main()

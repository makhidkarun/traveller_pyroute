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
        self.assertEqual(560, len(galaxy.stars_shadow), "Unexpected total world count after load")


if __name__ == '__main__':
    unittest.main()

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

        with self.assertRaises(Exception) as context:
            galaxy.read_sectors(delta, 'scaled', 'scaled')

        self.assertTrue('duplicated in sector Dagudashaag' in str(context.exception))


if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testDeltaGalaxy(baseTest):
    def test_read_sectors(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-spiked.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)

        with self.assertRaises(Exception) as context:
            galaxy.read_sectors(delta, 'scaled', 'scaled',
                                10, 'trade', 8, 1, False)

        self.assertTrue('duplicated in sector Dagudashaag' in str(context.exception))


if __name__ == '__main__':
    unittest.main()

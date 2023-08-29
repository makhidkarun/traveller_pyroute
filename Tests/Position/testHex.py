"""
Created on Aug 29, 2023

@author: CyberiaResurrection
"""
import unittest

from PyRoute.Galaxy import Sector
from PyRoute.Position.Hex import Hex


class TestHex(unittest.TestCase):
    def setUp(self):
        self.coreSector = Sector(' Core', ' 0, 0')
        self.lishunSector = Sector('Lishun', ' 0, 1')
        self.daguSector = Sector('Dagudashaag', ' -1, 0')
        self.fornastSector = Sector('Fornast', ' 1, 0')
        self.massiliaSector = Sector('Massilia', ' 0, -1')

    def testSetupOddColEvenRow(self):
        pos = Hex(self.coreSector, "0140")
        self.assertEqual(40, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(0, pos.r)
        self.assertEqual(0, pos.q)

    def testSetupEvenColEvenRow(self):
        pos = Hex(self.coreSector, "0220")
        self.assertEqual(20, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(19, pos.r)
        self.assertEqual(1, pos.q)

    def testSetupOddColOddRow(self):
        pos = Hex(self.coreSector, "0137")
        self.assertEqual(37, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(3, pos.r)
        self.assertEqual(0, pos.q)

    def testSetupEvenColOddRow(self):
        pos = Hex(self.coreSector, "0221")
        self.assertEqual(21, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(18, pos.r)
        self.assertEqual(1, pos.q)

    def testLishun(self):
        pos1 = Hex(self.lishunSector, "0140")
        pos2 = Hex(self.lishunSector, "0220")
        pos3 = Hex(self.lishunSector, "0137")
        pos4 = Hex(self.lishunSector, "0221")

        self.assertEqual(40, pos1.r)
        self.assertEqual(0, pos1.q)
        self.assertEqual(59, pos2.r)
        self.assertEqual(1, pos2.q)
        self.assertEqual(43, pos3.r)
        self.assertEqual(0, pos3.q)
        self.assertEqual(58, pos4.r)
        self.assertEqual(1, pos4.q)

    def testDaguSector(self):
        pos1 = Hex(self.daguSector, "0140")
        pos2 = Hex(self.daguSector, "0220")
        pos3 = Hex(self.daguSector, "0137")
        pos4 = Hex(self.daguSector, "0221")

        self.assertEqual(16, pos1.r)
        self.assertEqual(-32, pos1.q)
        self.assertEqual(35, pos2.r)
        self.assertEqual(-31, pos2.q)
        self.assertEqual(19, pos3.r)
        self.assertEqual(-32, pos3.q)
        self.assertEqual(34, pos4.r)
        self.assertEqual(-31, pos4.q)

    def testSectorDistances(self):
        pos1 = Hex(self.coreSector, "0140")
        pos2 = Hex(self.coreSector, "0220")
        pos3 = Hex(self.coreSector, "0137")
        pos4 = Hex(self.coreSector, "0221")

        self.assertEqual(0, pos1.distance(pos1))
        self.assertEqual(3, pos3.distance(pos1))
        self.assertEqual(3, pos1.distance(pos3))
        self.assertEqual(1, pos2.distance(pos4))
        self.assertEqual(1, pos4.distance(pos2))
        self.assertEqual(20, pos1.distance(pos2))
        self.assertEqual(19, pos1.distance(pos4))
        self.assertEqual(17, pos3.distance(pos2))
        self.assertEqual(16, pos3.distance(pos4))

    def testSectorCoreward(self):
        pos1 = Hex(self.coreSector, "0101")
        pos2 = Hex(self.lishunSector, "0140")

        self.assertEqual(39, pos1.r)
        self.assertEqual(0, pos1.q)

        self.assertEqual(40, pos2.r)
        self.assertEqual(0, pos2.q)
        self.assertEqual(1, pos1.distance(pos2))
        self.assertEqual(1, pos2.distance(pos1))

    def testSectorSpinward(self):
        pos1 = Hex(self.coreSector, "0110")
        pos2 = Hex(self.daguSector, "3210")

        self.assertEqual(1, pos1.distance(pos2))
        self.assertEqual(1, pos2.distance(pos1))

    def testSectorTrailing(self):
        pos1 = Hex(self.coreSector, "3220")
        pos2 = Hex(self.fornastSector, "0220")
        pos3 = Hex(self.fornastSector, "0219")
        pos4 = Hex(self.fornastSector, "0221")

        self.assertEqual(2, pos1.distance(pos2))
        self.assertEqual(2, pos1.distance(pos3))
        self.assertEqual(2, pos1.distance(pos4))

    def testSectorRimward(self):
        pos1 = Hex(self.coreSector, "1040")
        pos2 = Hex(self.massiliaSector, "1001")

        self.assertEqual(1, pos1.distance(pos2))

    def testSectorWideCoreward(self):
        pos1 = Hex(self.massiliaSector, "2101")
        pos2 = Hex(self.lishunSector, "2140")
        self.assertEqual(41, pos1.distance(pos2))

    def testFormatString(self):
        pos1 = Hex(self.coreSector, "2101")
        self.assertEqual("2101", str(pos1))
        pos2 = Hex(self.lishunSector, "0140")
        self.assertEqual("0140", str(pos2))

    def testNeighbors(self):
        pos1 = Hex(self.coreSector, "0505")

        self.assertEqual((4, 33), pos1.hex_position())
        self.assertEqual((5, 33), Hex.get_neighbor(pos1.hex_position(), 0))
        self.assertEqual((5, 32), Hex.get_neighbor(pos1.hex_position(), 1))
        self.assertEqual((4, 32), Hex.get_neighbor(pos1.hex_position(), 2))
        self.assertEqual((3, 33), Hex.get_neighbor(pos1.hex_position(), 3))
        self.assertEqual((3, 34), Hex.get_neighbor(pos1.hex_position(), 4))
        self.assertEqual((4, 34), Hex.get_neighbor(pos1.hex_position(), 5))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

"""
Created on Aug 29, 2023

@author: CyberiaResurrection
"""
import unittest

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Position.Hex import Hex
from PyRoute.Star import Star


class testHex(unittest.TestCase):
    def setUp(self):
        self.coreSector = Sector('# Core', '# 0, 0')
        self.lishunSector = Sector('# Lishun', '# 0, 1')
        self.daguSector = Sector('# Dagudashaag', '# -1, 0')
        self.fornastSector = Sector('# Fornast', '# 1, 0')
        self.massiliaSector = Sector('# Massilia', '# 0, -1')

    def testSetupOddColEvenRow(self):
        pos = Hex(self.coreSector, "0140")
        self.assertEqual(40, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(0, pos.r)
        self.assertEqual(0, pos.q)
        self.assertEqual(0, pos.x)
        self.assertEqual(0, pos.y)
        self.assertEqual(0, pos.z)
        self.assertEqual((0, 0), pos.hex_position())

    def testSetupEvenColEvenRow(self):
        pos = Hex(self.coreSector, "0220")
        self.assertEqual(20, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(19, pos.r)
        self.assertEqual(1, pos.q)
        self.assertEqual(1, pos.x)
        self.assertEqual(-20, pos.y)
        self.assertEqual(19, pos.z)
        self.assertEqual((1, 19), pos.hex_position())

    def testSetupOddColOddRow(self):
        pos = Hex(self.coreSector, "0137")
        self.assertEqual(37, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(3, pos.r)
        self.assertEqual(0, pos.q)
        self.assertEqual(0, pos.x)
        self.assertEqual(-3, pos.y)
        self.assertEqual(3, pos.z)
        self.assertEqual((0, 3), pos.hex_position())

    def testSetupEvenColOddRow(self):
        pos = Hex(self.coreSector, "0221")
        self.assertEqual(21, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(18, pos.r)
        self.assertEqual(1, pos.q)
        self.assertEqual(1, pos.x)
        self.assertEqual(-19, pos.y)
        self.assertEqual(18, pos.z)
        self.assertEqual((1, 18), pos.hex_position())

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

    def testCoreSector(self):
        pos = [
            Hex(self.coreSector, "0101"),
            Hex(self.coreSector, "0140"),
            Hex(self.coreSector, "3201"),
            Hex(self.coreSector, "3240"),
            Hex(self.coreSector, "1620")
        ]

        self.assertEqual(pos[0].hex_position(), (0, 39))
        self.assertEqual(pos[1].hex_position(), (0, 0))
        self.assertEqual(pos[2].hex_position(), (31, 23))
        self.assertEqual(pos[3].hex_position(), (31, -16))
        self.assertEqual(pos[4].hex_position(), (15, 12))

        for idx, (x, y) in enumerate([(1, 1), (1, 40), (32, 1), (32, 40), (16, 20)]):
            offset = Hex.dy_offset(y, (self.coreSector.dy // 40))
            q, r = Hex.hex_to_axial(x + self.coreSector.dx - 1, offset)
            self.assertEqual(pos[idx].hex_position(), (q, r))

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

        base_pos = pos1.hex_position()
        self.assertEqual((4, 33), base_pos)
        self.assertEqual((5, 5), Hex.axial_to_sector(4, 33))

        expected = [
            (0, (5, 32), (6, 5), "Down/right neighbour unexpected"),
            (1, (5, 33), (6, 4), "Up/right neighbour unexpected"),
            (2, (4, 34), (5, 4), "Up neighbour unexpected"),
            (3, (3, 34), (4, 4), "Up/left neighbour unexpected"),
            (4, (3, 33), (4, 5), "Down/left neighbour unexpected"),
            (5, (4, 32), (5, 6), "Down neighbour unexpected"),
        ]

        for direction, expected_hex, expected_sector, msg in expected:
            with self.subTest(msg):
                self.assertEqual(expected_hex, Hex.get_neighbor(base_pos, direction), msg)
                self.assertEqual(expected_sector, Hex.axial_to_sector(expected_hex[0], expected_hex[1]), msg + " sector")

    def test_auxiliary_distances(self):
        star1 = Star.parse_line_into_star(
            "2820 Ezevrtlad            C120000-B De Ba Po                            - -  - 900   Zh K2 III                      ",
            self.coreSector, 'fixed', 'fixed')

        star2 = Star.parse_line_into_star(
            "2323 Syss                 C400746-8 Na Va Pi                   { -1 } (A67-2) [6647] BD   S  - 510 5  ImDv M9 III D M5 V",
            self.lishunSector, 'fixed', 'fixed')

        exp_distance = 40
        heu_distance = Hex.heuristicDistance(star1, star2)
        self.assertEqual(exp_distance, heu_distance)
        hex_distance = star1.hex.hex_distance(star2.hex)
        self.assertEqual(exp_distance, hex_distance)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

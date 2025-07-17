"""
Created on Aug 29, 2023

@author: CyberiaResurrection
"""
import unittest

from AreaItems.Sector import Sector
from Position.Hex import Hex
from Star import Star


class testHex(unittest.TestCase):
    def setUp(self) -> None:
        self.coreSector = Sector('# Core', '# 0, 0')
        self.lishunSector = Sector('# Lishun', '# 0, 1')
        self.daguSector = Sector('# Dagudashaag', '# -1, 0')
        self.fornastSector = Sector('# Fornast', '# 1, 0')
        self.massiliaSector = Sector('# Massilia', '# 0, -1')
        self.antaresSector = Sector('# Antares', '# 1, 1')

    def testCoreSector(self) -> None:
        pos = self._generate_corner_hexes(self.coreSector)

        self.assertEqual(pos[0].hex_position(), (0, 39))
        self.assertEqual(pos[1].hex_position(), (0, 0))
        self.assertEqual(pos[2].hex_position(), (31, 23))
        self.assertEqual(pos[3].hex_position(), (31, -16))
        self.assertEqual(pos[4].hex_position(), (15, 12))

        self._check_corner_hexes(pos, self.coreSector)

    def testAntaresSector(self) -> None:
        pos = self._generate_corner_hexes(self.antaresSector)

        self.assertEqual(pos[0].hex_position(), (32, 63))
        self.assertEqual(pos[1].hex_position(), (32, 24))
        self.assertEqual(pos[2].hex_position(), (63, 47))
        self.assertEqual(pos[3].hex_position(), (63, 8))
        self.assertEqual(pos[4].hex_position(), (47, 36))

        self._check_corner_hexes(pos, self.antaresSector)

    def testFornast(self) -> None:
        pos = self._generate_corner_hexes(self.fornastSector)

        self.assertEqual(pos[0].hex_position(), (32, 23))
        self.assertEqual(pos[1].hex_position(), (32, -16))
        self.assertEqual(pos[2].hex_position(), (63, 7))
        self.assertEqual(pos[3].hex_position(), (63, -32))
        self.assertEqual(pos[4].hex_position(), (47, -4))

        self._check_corner_hexes(pos, self.fornastSector)

    def testSetupOddColEvenRow(self) -> None:
        pos = Hex(self.coreSector, "0140")
        self.assertEqual(40, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(0, pos.r)
        self.assertEqual(0, pos.q)
        self.assertEqual(0, pos.x)
        self.assertEqual(0, pos.y)
        self.assertEqual(0, pos.z)
        self.assertEqual((0, 0), pos.hex_position())

    def testSetupEvenColEvenRow(self) -> None:
        pos = Hex(self.coreSector, "0220")
        self.assertEqual(20, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(19, pos.r)
        self.assertEqual(1, pos.q)
        self.assertEqual(1, pos.x)
        self.assertEqual(-20, pos.y)
        self.assertEqual(19, pos.z)
        self.assertEqual((1, 19), pos.hex_position())

    def testSetupOddColOddRow(self) -> None:
        pos = Hex(self.coreSector, "0137")
        self.assertEqual(37, pos.row)
        self.assertEqual(1, pos.col)
        self.assertEqual(3, pos.r)
        self.assertEqual(0, pos.q)
        self.assertEqual(0, pos.x)
        self.assertEqual(-3, pos.y)
        self.assertEqual(3, pos.z)
        self.assertEqual((0, 3), pos.hex_position())

    def testSetupEvenColOddRow(self) -> None:
        pos = Hex(self.coreSector, "0221")
        self.assertEqual(21, pos.row)
        self.assertEqual(2, pos.col)
        self.assertEqual(18, pos.r)
        self.assertEqual(1, pos.q)
        self.assertEqual(1, pos.x)
        self.assertEqual(-19, pos.y)
        self.assertEqual(18, pos.z)
        self.assertEqual((1, 18), pos.hex_position())

    def testLishun(self) -> None:
        pos = self._generate_corner_hexes(self.lishunSector)

        self.assertEqual(pos[0].hex_position(), (0, 79))
        self.assertEqual(pos[1].hex_position(), (0, 40))
        self.assertEqual(pos[2].hex_position(), (31, 63))
        self.assertEqual(pos[3].hex_position(), (31, 24))
        self.assertEqual(pos[4].hex_position(), (15, 52))

        self._check_corner_hexes(pos, self.lishunSector)

    def testDaguSector(self) -> None:
        pos = self._generate_corner_hexes(self.daguSector)

        self.assertEqual(pos[0].hex_position(), (-32, 55))
        self.assertEqual(pos[1].hex_position(), (-32, 16))
        self.assertEqual(pos[2].hex_position(), (-1, 39))
        self.assertEqual(pos[3].hex_position(), (-1, 0))
        self.assertEqual(pos[4].hex_position(), (-17, 28))

        self._check_corner_hexes(pos, self.daguSector)

    def testCoreSector2(self) -> None:
        pos = self._generate_corner_hexes(self.coreSector)

        self.assertEqual(pos[0].hex_position(), (0, 39))
        self.assertEqual(pos[1].hex_position(), (0, 0))
        self.assertEqual(pos[2].hex_position(), (31, 23))
        self.assertEqual(pos[3].hex_position(), (31, -16))
        self.assertEqual(pos[4].hex_position(), (15, 12))

        self._check_corner_hexes(pos, self.coreSector)

    def testSectorDistances(self) -> None:
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

    def testSectorCoreward(self) -> None:
        pos1 = Hex(self.coreSector, "0101")
        pos2 = Hex(self.lishunSector, "0140")
        self.assertEqual(pos1.hex_position(), (0, 39))
        self.assertEqual(pos2.hex_position(), (0, 40))
        self.assertEqual(1, pos1.distance(pos2))
        self.assertEqual(1, pos2.distance(pos1))

    def testSectorSpinward(self) -> None:
        pos1 = Hex(self.coreSector, "0110")
        pos2 = Hex(self.daguSector, "3210")

        self.assertEqual(pos1.hex_position(), (0, 30))
        self.assertEqual(pos2.hex_position(), (-1, 30))

        self.assertEqual(1, pos1.distance(pos2))
        self.assertEqual(1, pos2.distance(pos1))

    def testSectorTrailing(self) -> None:
        pos1 = Hex(self.coreSector, "3220")
        pos2 = Hex(self.fornastSector, "0220")
        pos3 = Hex(self.fornastSector, "0219")
        pos4 = Hex(self.fornastSector, "0221")

        self.assertEqual(2, pos1.distance(pos2))
        self.assertEqual(2, pos1.distance(pos3))
        self.assertEqual(2, pos1.distance(pos4))

    def testSectorRimward(self) -> None:
        pos1 = Hex(self.coreSector, "1040")
        pos2 = Hex(self.massiliaSector, "1001")

        self.assertEqual(1, pos1.distance(pos2))

    def testSectorWideCoreward(self) -> None:
        pos1 = Hex(self.massiliaSector, "2101")
        pos2 = Hex(self.lishunSector, "2140")
        self.assertEqual(41, pos1.distance(pos2))

    def testFormatString(self) -> None:
        pos1 = Hex(self.coreSector, "2101")
        self.assertEqual("2101", str(pos1))
        pos2 = Hex(self.lishunSector, "0140")
        self.assertEqual("0140", str(pos2))

    def testNeighbors(self) -> None:
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

    def testFindNeighborOdd(self) -> None:
        center = Hex(self.coreSector, "0505")
        up = Hex(self.coreSector, "0504")
        down = Hex(self.coreSector, "0506")
        upLeft = Hex(self.coreSector, "0404")
        downLeft = Hex(self.coreSector, "0405")
        upRight = Hex(self.coreSector, "0604")
        downRight = Hex(self.coreSector, "0605")

        self.assertEqual(Hex.get_neighbor(center.hex_position(), 2), up.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 5), down.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 3), upLeft.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 4), downLeft.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 1), upRight.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 0), downRight.hex_position())

    def testFindNeighborEven(self) -> None:
        center = Hex(self.coreSector, "0202")
        down = Hex(self.coreSector, "0203")
        up = Hex(self.coreSector, "0201")
        upLeft = Hex(self.coreSector, "0102")
        downLeft = Hex(self.coreSector, "0103")
        upRight = Hex(self.coreSector, "0302")
        downRight = Hex(self.coreSector, "0303")

        self.assertEqual(Hex.get_neighbor(center.hex_position(), 2), up.hex_position())
        self.assertEqual(Hex.get_neighbor(up.hex_position(), 5), center.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 5), down.hex_position())
        self.assertEqual(Hex.get_neighbor(down.hex_position(), 2), center.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 1), upRight.hex_position())
        self.assertEqual(Hex.get_neighbor(upRight.hex_position(), 4), center.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 0), downRight.hex_position())
        self.assertEqual(Hex.get_neighbor(downRight.hex_position(), 3), center.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 4), downLeft.hex_position())
        self.assertEqual(Hex.get_neighbor(downLeft.hex_position(), 1), center.hex_position())
        self.assertEqual(Hex.get_neighbor(center.hex_position(), 3), upLeft.hex_position())
        self.assertEqual(Hex.get_neighbor(upLeft.hex_position(), 0), center.hex_position())

    def test_auxiliary_distances(self) -> None:
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

    def _generate_corner_hexes(self, sector: Sector) -> list[Hex]:
        pos = [
            Hex(sector, "0101"),
            Hex(sector, "0140"),
            Hex(sector, "3201"),
            Hex(sector, "3240"),
            Hex(sector, "1620")
        ]
        return pos

    def _check_corner_hexes(self, pos: list[Hex], sector: Sector) -> None:
        for idx, (x, y) in enumerate([(1, 1), (1, 40), (32, 1), (32, 40), (16, 20)]):
            offset = Hex.dy_offset(y, (sector.dy // 40))
            q, r = Hex.hex_to_axial(x + sector.dx - 1, offset)
            self.assertEqual(pos[idx].hex_position(), (q, r))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

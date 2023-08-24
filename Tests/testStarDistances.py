import unittest

from PyRoute.Galaxy import Sector
from PyRoute.Star import Star

distance_list = [
    ('0104, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0104', '2209', 21, 5, 21),
    ('0104, Lishun, big odd dx, odd dy', ' Lishun', ' 0, 1', '0104', '2209', 21, 5, 21),
    ('0105, Core, even dx, big even dy', ' Core', ' 0, 0', '0105', '0525', 4, 20, 22),
    ('0105, Vland, even dx, big even dy', ' Vland', ' -1, 1', '0105', '0525', 4, 20, 22),
    ('0205, Core, odd dx, even dy', ' Core', ' 0, 0', '0205', '1315', 11, 10, 15),
    ('0205, Dagudashaag, odd dx, even dy', ' Dagudashaag', ' -1, 0', '0205', '1315', 11, 10, 15),
    ('0204, Core, even dx, odd dy', ' Core', ' 0, 0', '0204', '1215', 10, 11, 16),
    ('0204, Zarushagar, even dx, odd dy', ' Zarushagar', ' -1, -1', '0204', '1215', 10, 11, 16),
    ('0105, Core, odd dx, odd dy', ' Core', ' 0, 0', '0105', '1216', 11, 11, 18),
    ('0105, Massilia, odd dx, odd dy', ' Massilia', ' 0, -1', '0105', '1216', 11, 11, 18),
    ('0204, Core, big even dx, even dy', ' Core', ' 0, 0', '0204', '2208', 20, 4, 20),
    ('0204, Delphi, big even dx, even dy', ' Delphi', ' 1, -1', '0204', '2208', 20, 4, 20),
    ('0204, Core, odd dx, big odd dy', ' Core', ' 0, 0', '0204', '0725', 5, 21, 23),
    ('0204, Fornast, odd dx, big odd dy', ' Fornast', ' 1, 0', '0204', '0725', 5, 21, 23),
    ('0105, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0105', '2210', 21, 5, 21),
    ('0105, Antares, big odd dx, odd dy', ' Antares', ' 1, 1', '0105', '2210', 21, 5, 21),
    ('0910, Core, odd-radius upper hexagon vertex', ' Core', ' 0, 0', '0910', '1407', 5, -3, 5),
    ('0910, Core, even-radius upper hexagon vertex', ' Core', ' 0, 0', '0910', '1507', 6, -3, 6),
    ('0910, Core, odd-radius lower hexagon vertex', ' Core', ' 0, 0', '0910', '1412', 5, 2, 10),
    ('0910, Core, even-radius lower hexagon vertex', ' Core', ' 0, 0', '0910', '1513', 6, 3, 12),
    ('0910, Core, odd-radius bottom vertex', ' Core', ' 0, 0', '0910', '0915', 0, 5, 5),
    ('0910, Core, even-radius bottom vertex', ' Core', ' 0, 0', '0910', '0916', 0, 6, 6),
    ('0910, Core, odd-radius middle hexagon side', ' Core', ' 0, 0', '0910', '1410', 5, 0, 5),
    ('0910, Core, even-radius middle hexagon side', ' Core', ' 0, 0', '0910', '1510', 6, 0, 6)
]

class testStarDistances(unittest.TestCase):
    def test_straight_distance(self):
        for blurb, sectorname, sectorloc, starthex, finhex, dx, dy, expected_straight_distance in distance_list:
            with self.subTest(msg=blurb):
                sector = Sector(sectorname, sectorloc)

                basex = int(starthex[0:2])
                basey = int(starthex[2:])

                star1 = Star.parse_line_into_star(
                    starthex + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    sector, 'fixed', 'fixed')

                newx = basex + dx
                newy = basey + dy
                newpos = str(newx).rjust(2, '0') + str(newy).rjust(2, '0')
                self.assertEqual(finhex, newpos, "Unexpected target hex")

                star2 = Star.parse_line_into_star(
                    newpos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    sector, 'fixed', 'fixed')

                fwd_distance = star1.distance(star2)
                self.assertEqual(expected_straight_distance, fwd_distance, "Unexpected forward distance between " + starthex + " and " + newpos)
                rev_distance = star2.distance(star1)
                self.assertEqual(expected_straight_distance, rev_distance, "Unexpected reverse distance between " + starthex + " and " + newpos)


if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.Galaxy import Sector
from PyRoute.Star import Star

distance_list = [
    ('0104, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0104', '2209', 21, 5, 37, 37),
    ('0105, Core, even dx, big even dy', ' Core', ' 0, 0', '0105', '0525', 4, 20, 26, 26),
    ('0205, Core, odd dx, even dy', ' Core', ' 0, 0', '0205', '1315', 11, 10, 25, 25),
    ('0204, Core, even dx, odd dy', ' Core', ' 0, 0', '0204', '1215', 10, 11, 25, 26),
    ('0105, Core, odd dx, odd dy', ' Core', ' 0, 0', '0105', '1216', 11, 11, 28, 28),
    ('0204, Core, big even dx, even dy', ' Core', ' 0, 0', '0204', '2208', 20, 4, 33, 34),
    ('0204, Core, odd dx, big odd dy', ' Core', ' 0, 0', '0204', '0725', 5, 21, 28, 28),
    ('0105, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0105', '2210', 21, 5, 37, 37)
]

class testStarDistances(unittest.TestCase):
    def test_straight_distance(self):
        for blurb, sectorname, sectorloc, starthex, finhex, dx, dy, expected_forward, expected_reverse in distance_list:
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
                self.assertEqual(expected_forward, fwd_distance, "Unexpected forward distance between " + starthex + " and " + newpos)
                rev_distance = star2.distance(star1)
                self.assertEqual(expected_reverse, rev_distance, "Unexpected reverse distance between " + starthex + " and " + newpos)


if __name__ == '__main__':
    unittest.main()

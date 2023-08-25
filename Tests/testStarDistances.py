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

inter_distance_list = [
    ("odd", "even", "even", "odd", -2, 0, "delta", "alpha"),
    ("odd", "odd", "odd", "even", +1, -2, "beta", "beta"),
    ("even", "odd", "even", "even", -2, -1, "alpha", "delta"),
    ("even", "even", "odd", "odd", 0, +2, "gamma", "gamma"),
    ("even", "even", "odd", "even", -1, +1, "alpha", "alpha"),
    ("odd", "odd", "even", "odd", -1, 0, "beta", "delta"),
    ("odd", "odd", "even", "even", +2, +1, "delta", "gamma"),
    ("even", "even", "odd", "odd", 0, -1, "delta", "beta"),
    ("odd", "odd", "even", "even", 0, -2, "gamma", "delta"),
    ("even", "even", "odd", "odd", +2, -2, "alpha", "alpha"),
    ("odd", "even", "even", "even", +2, +2, "beta", "beta"),
    ("even", "odd", "odd", "odd", -2, -2, "beta", "gamma"),
    ("even", "even", "odd", "odd", -2, +1, "gamma", "beta"),
    ("odd", "even", "even", "odd", -1, -2, "delta", "beta"),
    ("even", "even", "even", "odd", +1, +2, "delta", "delta"),
    ("odd", "odd", "even", "even", +1, -1, "gamma", "alpha"),
    ("even", "odd", "even", "even", 0, +1, "beta", "alpha"),
    ("even", "even", "odd", "even", +1, 0, "alpha", "gamma"),
    ("odd", "odd", "even", "even", -2, +2, "alpha", "alpha"),
    ("even", "odd", "odd", "odd", +2, -1, "beta", "delta"),
    ("even", "even", "even", "even", +2, 0, "gamma", "beta"),
    ("even", "odd", "even", "odd", -1, -1, "gamma", "gamma"),
    ("even", "even", "odd", "even", -1, +2, "alpha", "beta"),
    ("odd", "odd", "even", "even", 0, +1, "alpha", "delta"),
    ("odd", "even", "odd", "odd", +1, +1, "delta", "alpha")
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

    def test_intersector_straight_distance(self):
        sector_dict = dict()
        sector_dict[(-2, 0)] = 'Pliabriebl'
        sector_dict[(-2, 1)] = 'Tsadra Davr'
        sector_dict[(-2, 2)] = 'Chiep Zhez'
        sector_dict[(-2, -1)] = 'Brieplanz'
        sector_dict[(-2, -2)] = 'Viajlefliez'
        sector_dict[(-1, 0)] = 'Eiaplial'
        sector_dict[(-1, 1)] = 'Tsadra'
        sector_dict[(-1, 2)] = 'Shiants'
        sector_dict[(-1, -1)] = 'Sidiadl'
        sector_dict[(-1, -2)] = 'Bleblqansh'
        sector_dict[(0, 0)] = 'Zhdant'
        sector_dict[(0, 1)] = 'Zdiedeiant'
        sector_dict[(0, 2)] = 'Driasera'
        sector_dict[(0, -1)] = 'Yiklerzdanzh'
        sector_dict[(0, -2)] = 'Chtedrdia'
        sector_dict[(1, 0)] = 'Tienspevnekr'
        sector_dict[(1, 1)] = 'Stiatlchepr'
        sector_dict[(1, 2)] = 'Dalchie Jdatl'
        sector_dict[(1, -1)] = 'Afachtiabr'
        sector_dict[(1, -2)] = 'Steblenzh'
        sector_dict[(2, 0)] = 'Ziafrplians'
        sector_dict[(2, 1)] = 'Iakr'
        sector_dict[(2, 2)] = 'Zhdiakitlatl'
        sector_dict[(2, -1)] = 'Itvikiastaf'
        sector_dict[(2, -2)] = 'Chit Botshti'

        system_base = dict()
        system_base['alpha'] = (8, 10)
        system_base['beta'] = (24, 10)
        system_base['gamma'] = (8, 30)
        system_base['delta'] = (24, 30)

        zhdant_offset = (-7, +2)

        for source_x, source_y, target_x, target_y, sector_x, sector_y, source_quad, target_quad in inter_distance_list:
            source_secname = " Zhdant"
            sourcesectorloc = ' -7, 2'
            target_secname = ' ' + sector_dict[(sector_x, sector_y)]
            sector_offset = (zhdant_offset[0] + sector_x, zhdant_offset[1] + sector_y)
            targetsectorloc = ' ' + str(sector_offset[0]) + ', ' + str(sector_offset[1])
            source_raw = system_base[source_quad]
            source_star = (source_raw[0] + (1 if source_x == "odd" else 0), source_raw[1] + (1 if source_y == "odd" else 0))
            target_raw = system_base[target_quad]
            target_star = (target_raw[0] + (1 if target_x == "odd" else 0), target_raw[1] + (1 if target_y == "odd" else 0))
            source_hex = str(source_star[0]).rjust(2, '0') + str(source_star[1]).rjust(2, '0')
            target_hex = str(target_star[0]).rjust(2, '0') + str(target_star[1]).rjust(2, '0')
            source_name = source_secname + ' ' + source_hex
            target_name = target_secname + ' ' + target_hex
            blurb = source_name + ", " + target_name
            with self.subTest(msg=blurb):
                source_sector = Sector(source_secname, sourcesectorloc)
                self.assertEqual(-224, source_sector.dx, "Unexpected Zhdant sector dx value")
                self.assertEqual(80, source_sector.dy, "Unexpected Zhdant sector dx value")
                target_sector = Sector(target_secname, targetsectorloc)
                self.assertEqual(sector_offset[0] * 32, target_sector.dx,
                                 "Unexpected " + target_secname + " sector dx value")
                self.assertEqual(sector_offset[1] * 40, target_sector.dy,
                                 "Unexpected " + target_secname + " sector dy value")

                star1 = Star.parse_line_into_star(
                    source_hex + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    source_sector, 'fixed', 'fixed')
                self.assertEqual(source_star[0], star1.col, "Unexpected col value for " + source_name)
                self.assertEqual(source_star[1], star1.row, "Unexpected row value for " + source_name)

                star2 = Star.parse_line_into_star(
                    target_hex + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    target_sector, 'fixed', 'fixed')
                self.assertEqual(target_star[0], star2.col, "Unexpected col value for " + target_name)
                self.assertEqual(target_star[1], star2.row, "Unexpected row value for " + target_name)

                hexdist = star1.hex_distance(star2)
                straight_dist, raw_dx, raw_dy, dx, dy = star1.distance(star2, diagnostic=True)
                rev_straight_dist = star2.distance(star1)
                self.assertEqual(straight_dist, rev_straight_dist, "Straight distance should not be direction sensitive")
                msg = "Straight distance " + str(straight_dist) + " not equal to hex distance " + str(hexdist)
                gubbins = "Raw dx: " + str(raw_dx) + ", raw dy: " + str(raw_dy) + ", dx: " + str(dx) + ", dy: " + str(dy)
                self.assertEqual(hexdist, straight_dist, msg + "\n" + gubbins)


if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.Galaxy import Sector
from PyRoute.Star import Star

distance_list = [
    ('0104, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0104', '2209', 21, 5, 21),
    ('0104, Lishun, big odd dx, odd dy', ' Lishun', ' 0, 1', '0104', '2209', 21, 5, 21),
    ('0105, Core, even dx, big even dy', ' Core', ' 0, 0', '0105', '0525', 4, 20, 22),
    ('0105, Vland, even dx, big even dy', ' Vland', ' -1, 1', '0105', '0525', 4, 20, 22),
    ('0205, Core, odd dx, even dy', ' Core', ' 0, 0', '0205', '1315', 11, 10, 16),
    ('0205, Dagudashaag, odd dx, even dy', ' Dagudashaag', ' -1, 0', '0205', '1315', 11, 10, 16),
    ('0204, Core, even dx, odd dy', ' Core', ' 0, 0', '0204', '1215', 10, 11, 16),
    ('0204, Zarushagar, even dx, odd dy', ' Zarushagar', ' -1, -1', '0204', '1215', 10, 11, 16),
    ('0105, Core, odd dx, odd dy', ' Core', ' 0, 0', '0105', '1216', 11, 11, 16),
    ('0105, Massilia, odd dx, odd dy', ' Massilia', ' 0, -1', '0105', '1216', 11, 11, 16),
    ('0204, Core, big even dx, even dy', ' Core', ' 0, 0', '0204', '2208', 20, 4, 20),
    ('0204, Delphi, big even dx, even dy', ' Delphi', ' 1, -1', '0204', '2208', 20, 4, 20),
    ('0204, Core, odd dx, big odd dy', ' Core', ' 0, 0', '0204', '0725', 5, 21, 24),
    ('0204, Fornast, odd dx, big odd dy', ' Fornast', ' 1, 0', '0204', '0725', 5, 21, 24),
    ('0105, Core, big odd dx, odd dy', ' Core', ' 0, 0', '0105', '2210', 21, 5, 21),
    ('0105, Antares, big odd dx, odd dy', ' Antares', ' 1, 1', '0105', '2210', 21, 5, 21),
    ('0910, Core, odd-radius upper hexagon vertex', ' Core', ' 0, 0', '0910', '1407', 5, -3, 5),
    ('0910, Core, even-radius upper hexagon vertex', ' Core', ' 0, 0', '0910', '1507', 6, -3, 6),
    ('0910, Core, odd-radius lower hexagon vertex', ' Core', ' 0, 0', '0910', '1412', 5, 2, 5),
    ('0910, Core, even-radius lower hexagon vertex', ' Core', ' 0, 0', '0910', '1513', 6, 3, 6),
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

    def test_core_0101(self):
        sector = Sector('Core', ' 0, 0')
        starline = '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(0, star.q, "Origin should have zero q value")
        self.assertEqual(39, star.r, "Origin should have 39 r value")

    def test_core_0140(self):
        origin = Star.parse_line_into_star(
            '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V',
            Sector('Core', ' 0, 0'), 'fixed', 'fixed'
        )

        sector = Sector('Core', ' 0, 0')
        starline = '0140 Reference            B100727-C Na Va Pi RsA Ab                      { 3 }  (B6D+3) [7A5C] BD    NS - 302 12 ImDc K0 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(39, abs(origin.r - star.r), "Unexpected r offset")
        self.assertEqual(0, star.q, "Star should have zero q value")
        self.assertEqual(0, star.r, "Star should have 0 r value")

    def test_lishun_0101(self):
        origin = Star.parse_line_into_star(
            '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V',
            Sector('Core', ' 0, 0'), 'fixed', 'fixed'
        )

        sector = Sector('Lishun', ' 0, 1')
        starline = '0101 Ishimaga             A734433-9 Ni                       { 0 }  (933-3) [1426] B    -  - 603 10 ImDa K4 V M2 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(40, abs(origin.r - star.r), "Unexpected r offset")
        self.assertEqual(0, star.q, "Star should have zero q value")
        self.assertEqual(79, star.r, "Star should have 79 r value")

    def test_lishun_0140(self):
        origin = Star.parse_line_into_star(
            '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V',
            Sector('Core', ' 0, 0'), 'fixed', 'fixed'
        )

        sector = Sector('Lishun', ' 0, 1')
        starline = '0140 Vodyr                B782999-A Hi Pr                    { 3 }  (G8D+4) [AC6B] BcE  -  - 414 12 ImDa G8 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(1, abs(origin.r - star.r), "Unexpected r offset")
        self.assertEqual(0, star.q, "Star should have zero q value")
        self.assertEqual(40, star.r, "Star should have 40 r value")

    def test_massilia_0101(self):
        origin = Star.parse_line_into_star(
            '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V',
            Sector('Core', ' 0, 0'), 'fixed', 'fixed'
        )

        sector = Sector('Massilia', ' 0, -1')
        starline = '0101 Ishimaga             A734433-9 Ni                       { 0 }  (933-3) [1426] B    -  - 603 10 ImDa K4 V M2 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(40, abs(origin.r - star.r), "Unexpected r offset")
        self.assertEqual(0, star.q, "Star should have zero q value")
        self.assertEqual(-1, star.r, "Star should have -1 r value")

    def test_massilia_0140(self):
        origin = Star.parse_line_into_star(
            '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V',
            Sector('Core', ' 0, 0'), 'fixed', 'fixed'
        )

        sector = Sector('Massilia', ' 0, -1')
        starline = '0140 Sekeltin             B633447-B Ni Po Da                   { 1 }  (734+1) [455B] B    N  A 101 12 ImDc M2 V M4 V'

        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertEqual(79, abs(origin.r - star.r), "Unexpected r offset")
        self.assertEqual(0, star.q, "Star should have zero q value")
        self.assertEqual(-40, star.r, "Star should have -40 r value")

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
                hexdist = star1.hex_distance(star2)
                msg = "Straight distance " + str(fwd_distance) + " not equal to hex distance " + str(hexdist)
                self.assertEqual(hexdist, fwd_distance, msg)

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
                straight_dist = star1.distance(star2)
                rev_straight_dist = star2.distance(star1)
                self.assertEqual(straight_dist, rev_straight_dist, "Straight distance should not be direction sensitive")
                msg = "Straight distance " + str(straight_dist) + " not equal to hex distance " + str(hexdist)
                self.assertEqual(hexdist, straight_dist, msg)

    def test_trans_sector_border_distances_spinward_marches_to_gvurrdon(self):
        spin = Sector(' Spinward Marches', ' -4, 1')
        self.assertEqual(-128, spin.dx, "Unexpected sector dx")
        self.assertEqual(40, spin.dy, "Unexpected sector dy")
        gvur = Sector(' Gvurrdon', ' -4, 2')
        self.assertEqual(-128, gvur.dx, "Unexpected sector dx")
        self.assertEqual(80, gvur.dy, "Unexpected sector dy")

        for i in range(1, 33):
            with self.subTest(msg='Checking column ' + str(i)):
                spinpos = str(i).rjust(2, '0') + '01'
                gvurpos = str(i).rjust(2, '0') + '40'

                star1 = Star.parse_line_into_star(
                    spinpos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    spin, 'fixed', 'fixed')
                self.assertEqual(i, star1.col)
                self.assertEqual(1, star1.row)

                star2 = Star.parse_line_into_star(
                    gvurpos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    gvur, 'fixed', 'fixed')
                self.assertEqual(i, star2.col)
                self.assertEqual(40, star2.row)

                # Stars are immediately rimward/coreward of each other, so should have same q co-ord
                self.assertEqual(star1.q, star2.q, "q co-ords should match")

                self.assertEqual(1, star1.hex_distance(star2), 'Hex distance at ' + str(i) + ' is not 1 between ' + str(star1) + ' and ' + str(star2))
                self.assertEqual(1, star1.distance(star2), 'Straight distance at ' + str(i) + ' is not 1')

    def test_trans_sector_border_distances_core_to_massilia(self):
        core = Sector(' Core', ' 0, 0')
        self.assertEqual(0, core.dx, "Unexpected sector dx")
        self.assertEqual(0, core.dy, "Unexpected sector dy")
        mass = Sector(' Massilia', ' 0, -1')
        self.assertEqual(0, mass.dx, "Unexpected sector dx")
        self.assertEqual(-40, mass.dy, "Unexpected sector dy")

        for i in range(1, 33):
            with self.subTest(msg='Checking column ' + str(i)):
                masspos = str(i).rjust(2, '0') + '01'
                corepos = str(i).rjust(2, '0') + '40'

                star1 = Star.parse_line_into_star(
                    masspos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    mass, 'fixed', 'fixed')
                self.assertEqual(i, star1.col)
                self.assertEqual(1, star1.row)

                star2 = Star.parse_line_into_star(
                    corepos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    core, 'fixed', 'fixed')
                self.assertEqual(i, star2.col)
                self.assertEqual(40, star2.row)

                self.assertEqual(1, star1.hex_distance(star2), 'Hex distance at ' + str(i) + ' is not 1 ' + str(star1) + ' and ' + str(star2))
                self.assertEqual(1, star1.distance(star2), 'Straight distance at ' + str(i) + ' is not 1')

    def test_trans_sector_border_distances_massilia_to_diaspora(self):
        mass = Sector(' Massilia', ' 0, -1')
        self.assertEqual(0, mass.dx, "Unexpected sector dx")
        self.assertEqual(-40, mass.dy, "Unexpected sector dy")
        dias = Sector(' Diaspora', ' 0, -2')
        self.assertEqual(0, dias.dx, "Unexpected sector dx")
        self.assertEqual(-80, dias.dy, "Unexpected sector dy")

        for i in range(1, 33):
            with self.subTest(msg='Checking column ' + str(i)):
                diaspos = str(i).rjust(2, '0') + '01'
                masspos = str(i).rjust(2, '0') + '40'

                star1 = Star.parse_line_into_star(
                    diaspos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    dias, 'fixed', 'fixed')
                self.assertEqual(i, star1.col)
                self.assertEqual(1, star1.row)

                star2 = Star.parse_line_into_star(
                    masspos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    mass, 'fixed', 'fixed')
                self.assertEqual(i, star2.col)
                self.assertEqual(40, star2.row)

                self.assertEqual(1, star1.hex_distance(star2), 'Hex distance at ' + str(i) + ' is not 1 ' + str(star1) + ' and ' + str(star2))
                self.assertEqual(1, star1.distance(star2), 'Straight distance at ' + str(i) + ' is not 1')

    def test_trans_sector_border_distances_core_to_dagudashaag(self):
        core = Sector(' Core', ' 0, 0')
        self.assertEqual(0, core.dx, "Unexpected sector dx")
        self.assertEqual(0, core.dy, "Unexpected sector dy")
        dagu = Sector(' Dagudashaag', ' -1, 0')
        self.assertEqual(-32, dagu.dx, "Unexpected sector dx")
        self.assertEqual(0, dagu.dy, "Unexpected sector dy")

        for i in range(1, 33):
            with self.subTest(msg='Checking column ' + str(i)):
                dagupos = '32' + str(i).rjust(2, '0')
                corepos = '01' + str(i).rjust(2, '0')

                star1 = Star.parse_line_into_star(
                    dagupos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    dagu, 'fixed', 'fixed')
                self.assertEqual(32, star1.col)
                self.assertEqual(i, star1.row)

                star2 = Star.parse_line_into_star(
                    corepos + " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    core, 'fixed', 'fixed')
                self.assertEqual(1, star2.col)
                self.assertEqual(i, star2.row)

                self.assertEqual(1, star1.hex_distance(star2), 'Hex distance at ' + str(i) + ' is not 1 ' + str(star1) + ' and ' + str(star2))
                self.assertEqual(1, star1.distance(star2), 'Straight distance at ' + str(i) + ' is not 1')

    def test_distance_from_core_0101(self):
        core = Sector(' Core', ' 0, 0')
        dagu = Sector(' Dagudashaag', ' -1, 0')
        vland = Sector(' Vland', ' -1, 1')
        lishun = Sector(' Lishun', ' 0, 1')

        starline = '0101 Irkigkhan            C9C4733-9 Fl                                   { 0 }  (E69-3) [4726] B     -  - 123 8  ImDc M2 V'

        base = Star.parse_line_into_star(starline, core, 'fixed', 'fixed')
        stub = " Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     "

        systems = [
            ('Lishun 0140 - 1pc', lishun, '0140', 1),
            ('Lishun 0240 - 1pc', lishun, '0240', 1),
            ('Core 0201 - 1pc', core, '0201', 1),
            ('Core 0102 - 1pc', core, '0102', 1),
            ('Dagudashaag 3201 - 1pc', dagu, '3201', 1),
            ('Vland 3240 - 1pc', vland, '3240', 1),
            ('Lishun 0139 - 2pc', lishun, '0139', 2),
            ('Lishun 0239 - 2pc', lishun, '0239', 2),
            ('Lishun 0340 - 2pc', lishun, '0340', 2),
            ('Core 0301 - 2pc', core, '0301', 2),
            ('Core 0302 - 2pc', core, '0302', 2),
            ('Core 0202 - 2pc', core, '0202', 2),
            ('Core 0103 - 2pc', core, '0103', 2),
            ('Dagudashaag 3202 - 2pc', dagu, '3202', 2),
            ('Dagudashaag 3102 - 2pc', dagu, '3102', 2),
            ('Dagudashaag 3101 - 2pc', dagu, '3101', 2),
            ('Vland 3140 - 2pc', vland, '3140', 2),
            ('Vland 3239 - 2pc', vland, '3239', 2),
            ('Lishun 0138 - 3pc', lishun, '0138', 3),
            ('Lishun 0238 - 3pc', lishun, '0238', 3),
            ('Lishun 0339 - 3pc', lishun, '0339', 3),
            ('Lishun 0439 - 3pc', lishun, '0439', 3),
            ('Lishun 0440 - 3pc', lishun, '0440', 3),
            ('Core 0401 - 3pc', core, '0401', 3),
            ('Core 0402 - 3pc', core, '0402', 3),
            ('Core 0303 - 3pc', core, '0303', 3),
            ('Core 0203 - 3pc', core, '0203', 3),
            ('Core 0104 - 3pc', core, '0104', 3),
            ('Dagudashaag 3203 - 3pc', dagu, '3203', 3),
            ('Dagudashaag 3103 - 3pc', dagu, '3103', 3),
            ('Dagudashaag 3002 - 3pc', dagu, '3002', 3),
            ('Dagudashaag 3001 - 3pc', dagu, '3001', 3),
            ('Vland 3040 - 3pc', vland, '3040', 3),
            ('Vland 3039 - 3pc', vland, '3039', 3),
            ('Vland 3139 - 3pc', vland, '3139', 3),
            ('Vland 3238 - 3pc', vland, '3238', 3),
        ]

        for blurb, sector, position, distance in systems:
            with self.subTest(msg=blurb):
                targstar = Star.parse_line_into_star(position + stub, sector, 'fixed', 'fixed')
                self.assertEqual(distance, base.hex_distance(targstar), "Forward hex distance unexpected")
                self.assertEqual(distance, targstar.hex_distance(base), "Reverse hex distance unexpected")
                self.assertEqual(distance, base.distance(targstar), "Forward straight distance unexpected")
                self.assertEqual(distance, targstar.distance(base), "Reverse straight distance unexpected")


if __name__ == '__main__':
    unittest.main()

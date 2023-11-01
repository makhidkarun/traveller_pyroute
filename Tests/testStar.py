"""
Created on Mar 7, 2014

@author: tjoneslo
"""
import logging
import copy
import time
import unittest
import re
import sys

from PyRoute.Position.Hex import Hex
from PyRoute.Calculation.TradeCalculation import TradeCalculation
from PyRoute.Galaxy import Allegiance
from PyRoute.StatCalculation import StatCalculation

sys.path.append('../PyRoute')
from PyRoute.Star import Star
from PyRoute.Galaxy import Sector, Galaxy


class TestStar(unittest.TestCase):

    def setUp(self):
        pass

    def testParseIrkigkhan(self):
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual('0103', star1.position)
        self.assertTrue(star1.q == 0 and star1.r == 37, "%s, %s" % (star1.q, star1.r))
        self.assertEqual('Irkigkhan', star1.name)
        self.assertEqual('C9C4733-9', str(star1.uwp))
        self.assertEqual('Im', star1.alg_code)
        self.assertEqual(10, star1.population, "Population %s" % star1.population)
        self.assertEqual(9, star1.wtn, "wtn %s" % star1.wtn)
        self.assertEqual('Fl', str(star1.tradeCode))
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertFalse(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertEqual(3, star1.ggCount)
        self.assertEqual('M2 V', str(star1.star_list_object))
        self.assertEqual(0, star1.x)
        self.assertEqual(-37, star1.y)
        self.assertEqual(37, star1.z)
        self.assertEqual(0, star1.q)
        self.assertEqual(37, star1.r)
        self.assertEqual(3, star1.row)
        self.assertEqual(1, star1.col)

    def testParseIrkigkhanRUCollapse(self):
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseIrkigkhanRUScaled(self):
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseShanaMa(self):
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual('0104', star1.position)
        self.assertTrue(star1.q == 0 and star1.r == 36, "%s, %s" % (star1.q, star1.r))
        self.assertEqual('Shana Ma', star1.name)
        self.assertEqual('E551112-7', str(star1.uwp))
        self.assertEqual('Im', star1.alg_code)
        self.assertEqual(0, star1.population, "Population %s" % star1.population)
        self.assertEqual(2, star1.wtn, "wtn %s" % star1.wtn)
        self.assertEqual('Lo Po', str(star1.tradeCode))
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertTrue(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertEqual(3, star1.ggCount)
        self.assertEqual(2, len(star1.star_list))
        self.assertEqual('K2 IV M7 V', str(star1.star_list_object))
        self.assertEqual(0, star1.x)
        self.assertEqual(-36, star1.y)
        self.assertEqual(36, star1.z)
        self.assertEqual(0, star1.q)
        self.assertEqual(36, star1.r)
        self.assertEqual(4, star1.row)
        self.assertEqual(1, star1.col)

    def testParseSyss(self):
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "2323 Syss                 C400746-8 Na Va Pi                   { -1 } (A67-2) [6647] BD   S  - 510 5  ImDv M9 III D M5 V",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual('2323', star1.position)
        self.assertEqual('Syss', star1.name)
        self.assertEqual('C400746-8', str(star1.uwp))
        self.assertEqual('Na Pi Va', str(star1.tradeCode))
        self.assertEqual('M9 III D M5 V', star1.stars)
        self.assertEqual('M9 III D M5 V', str(star1.star_list_object))
        self.assertEqual(22, star1.x)
        self.assertEqual(-28, star1.y)
        self.assertEqual(6, star1.z)
        self.assertEqual(22, star1.q)
        self.assertEqual(6, star1.r)
        self.assertEqual(23, star1.row)
        self.assertEqual(23, star1.col)

    def testParseZhdant(self):
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2719 Zhdant               A6547C8-F Ag An Cx                            - KM - 811   Zh K0 V                        ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Ag An Cx', str(star1.tradeCode))
        self.assertEqual(-198, star1.x)
        self.assertEqual(-2, star1.y)
        self.assertEqual(200, star1.z)
        self.assertEqual(-198, star1.q)
        self.assertEqual(200, star1.r)
        self.assertEqual(19, star1.row)
        self.assertEqual(27, star1.col)

    def testParseVlazzhden(self):
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2720 Vlazzhden            C210143-8 Lo Ni                               - -  - 303   Zh G1 IV                       ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Lo Ni', str(star1.tradeCode))
        self.assertEqual(-198, star1.x)
        self.assertEqual(-1, star1.y)
        self.assertEqual(199, star1.z)
        self.assertEqual(-198, star1.q)
        self.assertEqual(199, star1.r)
        self.assertEqual(20, star1.row)
        self.assertEqual(27, star1.col)

    def testParseTlapinsh(self):
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2819 Tlapinsh             B569854-C Ri                                  - -  - 622   Zh F7 V                        ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Ri', str(star1.tradeCode))
        self.assertEqual(-197, star1.x)
        self.assertEqual(-2, star1.y)
        self.assertEqual(199, star1.z)
        self.assertEqual(-197, star1.q)
        self.assertEqual(199, star1.r)
        self.assertEqual(19, star1.row)
        self.assertEqual(28, star1.col)

    def testParseEzevrtlad(self):
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2820 Ezevrtlad            C120000-B De Ba Po                            - -  - 900   Zh K2 III                      ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Ba De Po', str(star1.tradeCode))
        self.assertEqual(-197, star1.x)
        self.assertEqual(-1, star1.y)
        self.assertEqual(198, star1.z)
        self.assertEqual(-197, star1.q)
        self.assertEqual(198, star1.r)
        self.assertEqual(20, star1.row)
        self.assertEqual(28, star1.col)

    def testParseUnchin(self):
        sector = Sector('# Zarushagar', '# -1, -1')
        line = '0522 Unchin               A437743-E                            { 2 }  (B6D-1) [492B] B     N  - 620 9  ImDi K0 III                                                       '
        star1 = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)
        self.assertEqual('', str(star1.tradeCode))

    def testParseBarrelOfWeird(self):
        # These were weird intermediate values that _kept_ turning up in round-trip testing, so it was worth breaking it
        # out as a separate unit test to try to figure out _where_ they fire up the hyperdrive.
        weird_line = [
            ('0101 000000000000000      ???????-?                                       { -2 } (000-0) -      -    -  - 000 0  00  D                                                        ', ''),
            ('0110 000000000000000      ???????-?                                       { -2 } (000-0) -      Bc   -  - 000 0  00  D                                                        ', ''),
            ('0101 0                    A000000-0                                       { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V ', ''),
            ('0110 000000000000000 ???????-? 00000000000000( {1} (000-0)       -   - 0 000   00 D', '')
        ]
        sector = Sector('# Core', '# 0, 0')

        for base_line, expected_trade in weird_line:
            with self.subTest():
                star1 = Star.parse_line_into_star(base_line, sector, 'fixed', 'fixed')
                self.assertIsInstance(star1, Star)
                actual_trade = str(star1.tradeCode)
                self.assertEqual(expected_trade, actual_trade)

    def testParseLowercaseUWP(self):
        line = '0101 000000000000000 AffaFxj-z 000000000000000 {0} (000-0) [0000] - - 0 000   00 D'
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)
        self.assertEqual(33, star1.tl)
        expected_uwp = 'AFFAFXJ-Z'
        self.assertEqual(expected_uwp, str(star1.uwp), "Unexpected UWP value after parsing")

    def testParseExplicitHomeworlds(self):
        sector = Sector('# Core', '# 0, 0')

        homeworlds = [
            ('Terra', '1827 Terra                A867A69-F Hi Ga [Solomani] Dolp0 Mr       { 4 }  (H9C+4) [BE6G] BEf  NW - 114 10 ImDs G2 V                         ', ['Dolp0', 'SoloW'], 'Dolp0 Ga Hi Mr [Solomani]'),
            ('Vland', '1717 Vland                A967A9A-F Hi Cs [Vilani]            { 3 }  (D9F+5) [CD7H] BEFG N  - 310 7  ImDv F8 V           ', ['VilaW'], 'Cs Hi [Vilani]'),
            ('Kusyu', '1226 Kusyu                A876976-E Hi In Cx [Aslan]                       { 5 }  (F8H+4) [9E4D] - RT - 403 8  AsSc G4 V D             ', ['AslaW'], 'Cx Hi In [Aslan]'),
            ('Lair', '2402 Lair                 A8859B9-E Hi Ga Cx Pr Pz [Vargr] { 3 }  (F8F+4) [AC6F] - K  A 213 12 VLPr G5 V        ', ['VargW'], 'Cx Ga Hi Pr Pz [Vargr]')
        ]

        for msg, star_line, expected_sophonts, expected_trade in homeworlds:
            with self.subTest(msg):
                star1 = Star.parse_line_into_star(star_line, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = star1.alg_code
                self.assertIsInstance(star1, Star)
                self.assertTrue(star1.is_well_formed())

                self.assertEqual(expected_sophonts, star1.tradeCode.sophont_list)
                self.assertEqual(expected_trade, str(star1.tradeCode), 'Unexpected trade code list')

    def testParseStarlineWithOnlyKnownPhysicalsAndNoTradeCodes(self):
        starline = '3135                      ?478???-?                                     - - - ?02   Na'
        sector = Sector('# Core', '# 0, 0')

        star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)
        star1.index = 0
        star1.allegiance_base = star1.alg_code

        self.assertTrue(star1.is_well_formed())

    def testAPortModifier(self):
        # cwtn =[3,4,4,5,6,7,7,8,9,10,10,11,12,13,14,15]
        cwtn = [3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn * 3 + 13) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testBPortModifier(self):
        # cwtn =[2,3,4,5,5,6,7,8,8,9,10,11,11,12,12,13]
        cwtn = [2, 3, 4, 5, 5, 6, 7, 8, 8, 9, 10, 11, 11, 12, 13, 14]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn * 3 + 11) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testCPortModifier(self):
        cwtn = [2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 10, 11, 11, 12]
        for uwtn in range(15):
            if (uwtn > 9):
                wtn = int(round(max(0, (uwtn + 9) // 2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 9) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testDPortModifier(self):
        cwtn = [1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11]
        for uwtn in range(15):
            if (uwtn > 7):
                wtn = int(round(max(0, (uwtn + 7) // 2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 7) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testEPortModifier(self):
        cwtn = [1, 2, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10]
        for uwtn in range(15):
            if (uwtn > 5):
                wtn = int(round(max(0, (uwtn + 5) // 2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 5) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testXPortModifier(self):
        # cwtn =[0,1,2,3,0,0,0,1,1,2,2,3,3,4,4,5]
        cwtn = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn - 5) // 2)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testCalcTrade(self):
        self.assertEqual(TradeCalculation.calc_trade(0), 1)
        self.assertEqual(TradeCalculation.calc_trade(1), 5)
        self.assertEqual(TradeCalculation.calc_trade(2), 10)
        self.assertEqual(TradeCalculation.calc_trade(3), 50)
        self.assertEqual(TradeCalculation.calc_trade(4), 100)
        self.assertEqual(TradeCalculation.calc_trade(5), 500)
        self.assertEqual(TradeCalculation.calc_trade(6), 1000)

    def testPassengerBTN(self):
        self.assertEqual(TradeCalculation.calc_passengers(10), 0)
        self.assertEqual(TradeCalculation.calc_passengers(11), 5)
        self.assertEqual(TradeCalculation.calc_passengers(12), 10)
        self.assertEqual(TradeCalculation.calc_passengers(13), 50)
        self.assertEqual(TradeCalculation.calc_passengers(14), 100)
        self.assertEqual(TradeCalculation.calc_passengers(15), 500)

    def testHashValueSameAfterCaching(self):
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V  ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

        # Grabbing hash value twice, once to seed Star._hash, second to dig it out of that cache
        oldHash = star1.__hash__()
        newHash = star1.__hash__()
        self.assertEqual(oldHash, newHash)

    def testEquals(self):
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star3 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

        self.assertEqual(star1, star2)
        self.assertNotEqual(star1, star3)
        self.assertNotEqual(star2, star3)

    def testParseBespin(self):
        sector = Sector('# Core', '# 0, 0')
        line = '0615 Bespin II            EAA19AC-4 Fl Hi He In          {+0} (98b-1) [a935] - - - 223 9  Na G1 V           '
        star1 = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)
        self.assertEqual('Fl He Hi In', str(star1.tradeCode))
        self.assertEqual('(98B-1)', star1.economics)
        self.assertEqual('[A935]', star1.social)

    def testStarSize(self):
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

    def test_deep_copy(self):
        alg = Allegiance("am", "name")
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star1.index = 11
        star1.allegiance_base = alg
        star1.is_well_formed()

        starcopy = copy.deepcopy(star1)
        starcopy.is_well_formed()

        self.assertEqual(star1, starcopy)

    def test_ehex_to_numeric_mapping_for_TL_A_and_up(self):
        # shut up log output - is completely irrelevant
        logger = logging.getLogger('PyRoute.Star')
        logger.setLevel(logging.CRITICAL)

        # taken from https://travellermap.com/doc/secondsurvey#ehex
        ehex_map = [
            ('A', 10), ('B', 11), ('C', 12), ('D', 13), ('E', 14), ('F', 15), ('G', 16), ('H', 17), ('J', 18), ('K', 19),
            ('L', 20), ('M', 21), ('N', 22), ('P', 23), ('Q', 24), ('R', 25), ('S', 26), ('T', 27), ('U', 28), ('V', 29),
            ('W', 30), ('X', 31), ('Y', 32), ('Z', 33)
        ]

        for chunk in ehex_map:
            with self.subTest():
                letter = chunk[0]
                target = chunk[1]

                star1 = Star.parse_line_into_star(
                    "0104 Shana Ma             E551112-"+letter+" Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

                self.assertEqual(target, star1.tl, "Unexpected mapping for TL " + letter)

    def test_document_ehex_to_numeric_mapping_for_TL_I_and_O(self):
        # shut up log output - is completely irrelevant
        logger = logging.getLogger('PyRoute.Star')
        logger.setLevel(logging.CRITICAL)

        ehex_map = [
            ('I', 18), ('O', 22)
        ]

        for chunk in ehex_map:
            with self.subTest():
                letter = chunk[0]
                target = chunk[1]

                star1 = Star.parse_line_into_star(
                    "0104 Shana Ma             E551112-"+letter+" Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

                self.assertEqual(target, star1.tl, "Unexpected mapping for TL " + letter)

    def testCompareHexDistanceToAxialDistance(self):
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

        sector = Sector('# Zhdant', '# -7, 2')
        star2 = Star.parse_line_into_star(
            "2720 Vlazzhden            C210143-8 Lo Ni                               - -  - 303   Zh G1 IV                       ",
            sector, 'fixed', 'fixed')

        hex_dist = star1.hex.hex_distance(star2)
        axial_dist = Hex.axial_distance((star1.q, star1.r), (star2.q, star2.r))
        self.assertEqual(hex_dist, axial_dist, "Unexpected axial distance")
        distance = star1.distance(star2)
        self.assertEqual(hex_dist, distance, "Unexpected distance")

    def test_ehex_to_int_and_back(self):
        tech_list = [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            ('A', 10),
            ('B', 11),
            ('C', 12),
            ('D', 13),
            ('E', 14),
            ('F', 15),
            ('G', 16),
            ('H', 17),
            ('J', 18),
            ('K', 19),
            ('L', 20),
            ('M', 21),
            ('N', 22),
            ('P', 23),
            ('Q', 24),
            ('R', 25),
            ('S', 26),
            ('T', 27),
            ('U', 28),
            ('V', 29),
            ('W', 30),
            ('X', 31),
            ('Y', 32),
            ('Z', 33)
        ]

        for ehex, intvalue in tech_list:
            with self.subTest():
                star = Star()
                act_int = star._ehex_to_int(str(ehex))
                self.assertEqual(intvalue, act_int, "Ehex-to-int mapping failed for TL " + str(ehex))
                act_ehex = star._int_to_ehex(act_int)
                self.assertEqual(str(ehex), act_ehex, "Int-to-ehex mapping failed for TL " + str(ehex))

    def test_parse_to_line(self):
        line_list = [
            ("0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ", "K"),
            ("3030 Khaammumlar          E430761-6 De Na Po O:3032                       { -2 } (965-5) [3512] B    -  - 520 6  ImDv M0 V M5 V                                                ", "M"),
            ("1840 Mashuu               D725413-8 Ni                                    { -3 } (731-5) [1125] B    -  - 401 14 ImDv M0 V                                                     ", "M"),
            ("0101 000000000000000      ???????-?                                       { -2 } -       -      -    -  - 000 0  0000 D                                                        ", "D"),
            ("0101 000000000000000      ???????-?                                       { -2 } (731-5) [1125] -    -  - 000 0  0000 D                                                        ", "D"),
            ("0101 000000000000000      ???????-?                                       { -2 } -       [1125] -    -  - 000 0  0000 D                                                        ", "D"),
            ("0101 000000000000000      ???????-?                                       { -2 } (731-5) -      -    -  - 000 0  0000 D                                                        ", "D"),
            ("2132 Iyuok                C776951-A Hi In (Iyuok) Da Cx       {  3 } (98B+2) [CC1D] - N  A 500 5  Iy   F9 V M1 V", 'F'),
            ("2133                      C631563-6 Ni Po Cy O:2132 IyuokW Pz { -2 } (640+1) [4386] - N  A 515 14 Iy   K2 V", 'K'),
            ("0922 Celetron             A575242-F Lo RsO                               { 1 }  (611-3) [1319] B     N  - 302 8  ImDc M1 V            Xb:0622 Xb:1123", 'M'),
            ("1708                      E32579A-7 Pi X!tkW Pz                  { -2 } (761+2) [3566] - -  A 705 14 KkTw A0 V", 'A'),
            ("2926                      B8B2413-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M  A 514 16 HvFd G4 V M1 V", 'G'),
            ("1917 Iaplebl              XAD0000-0 Ba Sa                       {-3} (900-5) [0000] - -  - 023 10 NaXX M7 VI M9 VI", 'M'),
            ("2526 Shadowsand           C000416-B As Ni Va                      { 0 }  (733-1) [344A] - -  - 510 10 NaHu BH", 'BH'),
            ("1901                      D335213-6 Lo                            { -3 } (811+5) [1167] - -  - 723 13 HvFd G7 M4 V        ", 'G'),
            ("1317 Chegu                X544000-0 Ba Sa                       {-3} (800-5) [0000] - -  - 002 12 NaXX G8 V BD        ", 'G'),
            ("0620 Shajzdenchta         C5699DB-9 Hi Pr                { 1 }  (D89-3) [CA26] - -  - 123 14 ZhMe M9 V BD BD M3 VI            ", 'M'),
            ("0138 Plech-45             X574000-0 Ba                   { -3 } (800-3) [0000] - -  - 024 16 NaXX M1 V D BD BD              ", 'M')
        ]
        for line, expected_primary_type in line_list:
            with self.subTest():
                star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = star1.alg_code
                star1.is_well_formed()
                self.assertEqual(expected_primary_type, star1.primary_type, "Unexpected primary type")

                mid_line = star1.parse_to_line()
                # Not comparing mid_line to original because trade codes are re-ordered
                star2 = Star.parse_line_into_star(mid_line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                self.assertEqual(star1, star2, "Regenerated star does not equal original star")
                nu_line = star2.parse_to_line()
                self.assertEqual(mid_line, nu_line, "Regenerated star line does not match round-trip star line")
                self.assertEqual(expected_primary_type, star2.primary_type, "Unexpected primary type")

    def testShortSophontCodeIntoStatsCalculation(self):
        line = '2926                      B8B2613-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M  A 514 16 HvFd G4 V M1 V     '
        sector = Sector('# Phlask', '# 3,-3')

        star = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        star.index = 0
        star.allegiance_base = star.alg_code
        self.assertEqual(5, star.population, "Expected star population")
        result, msg = star.tradeCode.is_well_formed()
        self.assertTrue(result, msg)
        galaxy = Galaxy(0)
        stat_calc = StatCalculation(galaxy)

        stat_calc.add_pop_to_sophont(galaxy.stats, star)
        stats = galaxy.stats
        self.assertTrue('Hak' in stats.populations)
        self.assertTrue('Huma' in stats.populations)
        self.assertEqual(5, stats.populations['Hak'].population)
        self.assertEqual(0, stats.populations['Huma'].population)

    def testParseStarlineWithSomeUnknownUWPValues(self):
        # Unknown-socials lLifted from Kruse 0709 in Travmap M1105 data as at 12 Dec 2023
        # Port-known lifted from Kruse 1001 in Travmap M1105 data as at 12 Dec 2023
        # Port + size known lifted from Kruse 0302 in Travmap M1105 data as at 12 Dec 2023
        # Port thru atmo known lifted from Kruse 0310 in Travmap M1105 data as at 12 Dec 2023
        # Physicals known lifted from Un'k!!ng 1410 in Travmap M1105 data as at 12 Dec 2023, with star added
        sector = Sector('# Phlask', '# 3,-3')
        cases = [
            ('Unknown socials', '0709 Adams 0709           X344???-?                                       - - - 001   Na M6 V'),
            ('Port known', '1001 Barnett 0201         X??????-?                                       - - A 013   Na K4 V'),
            ('Port + size known', '0302 Adams 0302           X3?????-?                                       - - - 001   Na K6 V'),
            ('Port thru atmo known', '0310 Adams 0310           X41????-?                                       - - - 011   Na M3 V'),
            ('Physicals known', '1410                      ?200???-? Va                                  - - - ?24   Na M3 V')
        ]

        for msg, starline in cases:
            with self.subTest(msg):
                star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                self.assertIsNotNone(star, "Starline should parse cleanly")

    def test_owning_self_is_not_well_formed(self):
        line = '3138 Andula               C542468-8 He Ni Po O:3138                       { -2 } (931-2) [4258] B    -  - 121 9  ImDv G4 V'
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star1.index = 0
        star1.allegiance_base = star1.alg_code

        msg = None

        try:
            star1.is_well_formed(log=False)
        except AssertionError as e:
            msg = str(e)

        expected_msg = "Star " + str(star1.name) + " cannot own itself"
        self.assertEqual(expected_msg, msg)

    def test_colonising_self_is_not_well_formed(self):
        line = '3138 Andula               C542468-8 He Ni Po C:3138                       { -2 } (931-2) [4258] B    -  - 121 9  ImDv G4 V'
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star1.index = 0
        star1.allegiance_base = star1.alg_code

        msg = None

        try:
            star1.is_well_formed(log=False)
        except AssertionError as e:
            msg = str(e)

        expected_msg = "Star " + str(star1.name) + " cannot colonise itself"
        self.assertEqual(expected_msg, msg)

    def testParseAnjeChadr(self):
        line = '0123 Anje Chadr           B568778-A Ag Ri Sa C:0124            {+4 } (G6C+4) [4B38] - V  - 222 11 Zh K6 V'
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star1.index = 0
        star1.allegiance_base = star1.alg_code

        star1.is_well_formed(log=False)
        self.assertEqual(1, len(star1.tradeCode.colony))

    def testParseGlisten(self):
        line = '2036 Glisten              A000986-F As Hi In Na Va Cp                        { 5 }  (D8H+4) [8E4E] BEF   NS - 811 13 ImDd K9 V          '
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        star1.index = 0
        star1.allegiance_base = star1.alg_code

        star1.is_well_formed(log=False)

        parse_line = star1.parse_to_line()
        foo = 1


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

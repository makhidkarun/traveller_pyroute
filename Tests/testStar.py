"""
Created on Mar 7, 2014

@author: tjoneslo
"""
import logging
import copy
import unittest

from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Position.Hex import Hex
from PyRoute.Calculation.TradeCalculation import TradeCalculation
from PyRoute.StatCalculation.StatCalculation import StatCalculation

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Star import Star
from PyRoute.SystemData.UWP import UWP
from PyRoute.TradeCodes import TradeCodes


class TestStar(unittest.TestCase):

    def setUp(self) -> None:
        ParseStarInput.deep_space = {}
        pass

    def test_init_blank(self) -> None:
        star = Star()
        self.assertIsNone(star.sector)
        self.assertIsInstance(star.logger, logging.Logger)

    def test_getstate_blank(self) -> None:
        star = Star()
        state = star.__getstate__()
        exp_state = {'alg_base_code': None, 'alg_code': None, 'allegiance_base': None, 'baseCode': None, 'belts': None,
                     'budget': None, 'col_be': None, 'component': None, 'deep_space_station': False, 'economics': None,
                     'eti_cargo': None, 'eti_passenger': None, 'ggCount': None, 'gwp': None, 'hex': None, 'im_be': None,
                     'importance': None, 'index': None, 'is_enqueued': False, 'is_landmark': False, 'is_redzone': False,
                     'is_target': False, 'mspr': None, 'name': None, 'nobles': None, 'ownedBy': None, 'passIn': None,
                     'passOver': None, 'perCapita': None, 'popM': None, 'population': None, 'position': None,
                     'raw_be': None, 'routes': None, 'ru': None, 'ship_capacity': None, 'social': None,
                     'star_list_object': None, 'starportBudget': None, 'starportPop': None, 'starportSize': None,
                     'stars': None, 'suppress_soph_percent_warning': False, 'tcs_gwp': None, 'tradeCode': None,
                     'tradeCount': None, 'tradeIn': None, 'tradeOver': None, 'trade_cost': 0.0, 'trade_id': '',
                     'uwp': None, 'uwpCodes': None, 'worlds': None, 'wtn': None, 'zone': None}

        self.assertEqual(exp_state, state)

    def testParseIrkigkhan(self) -> None:
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

    def test_calc_hash(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        exp_key = ('0103', 'Irkigkhan', 'C9C4733-9', 'Core')
        self.assertEqual(exp_key, star1._key)
        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')
        exp_key = ('0104', 'Shana Ma', 'E551112-7', 'Core')
        self.assertEqual(exp_key, star2._key)
        star1.calc_hash()
        star2.calc_hash()
        self.assertNotEqual(star1.__hash__(), star2.__hash__())

    def testParseIrkigkhanRUCollapse(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseIrkigkhanRUScaled(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseShanaMa(self) -> None:
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

    def testParseSyss(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "2323 Syss                 C400746-8 Na Va Pi                   { -1 } (A67-2) [6647] BD   S  - 510 5  ImDv M9 III D M5 V",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual(star1.position, '2323')
        self.assertEqual(star1.name, 'Syss')
        self.assertEqual('C400746-8', str(star1.uwp))
        self.assertEqual(star1.stars, 'M9 III D M5 V')
        self.assertEqual('M9 III D M5 V', str(star1.star_list_object))
        self.assertEqual(22, star1.x)
        self.assertEqual(-28, star1.y)
        self.assertEqual(6, star1.z)
        self.assertEqual(22, star1.q)
        self.assertEqual(6, star1.r)
        self.assertEqual(23, star1.row)
        self.assertEqual(23, star1.col)

    def testParseZhdant(self) -> None:
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2719 Zhdant               A6547C8-F Ag An Cx                            - KM - 811   Zh K0 V                        ",
            sector, 'fixed', 'fixed')

        self.assertEqual(-198, star1.x)
        self.assertEqual(-2, star1.y)
        self.assertEqual(200, star1.z)
        self.assertEqual(-198, star1.q)
        self.assertEqual(200, star1.r)
        self.assertEqual(19, star1.row)
        self.assertEqual(27, star1.col)

    def testParseVlazzhden(self) -> None:
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2720 Vlazzhden            C210143-8 Lo Ni                               - -  - 303   Zh G1 IV                       ",
            sector, 'fixed', 'fixed')

        self.assertEqual(-198, star1.x)
        self.assertEqual(-1, star1.y)
        self.assertEqual(199, star1.z)
        self.assertEqual(-198, star1.q)
        self.assertEqual(199, star1.r)
        self.assertEqual(20, star1.row)
        self.assertEqual(27, star1.col)

    def testParseTlapinsh(self) -> None:
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2819 Tlapinsh             B569854-C Ri                                  - -  - 622   Zh F7 V                        ",
            sector, 'fixed', 'fixed')

        self.assertEqual(-197, star1.x)
        self.assertEqual(-2, star1.y)
        self.assertEqual(199, star1.z)
        self.assertEqual(-197, star1.q)
        self.assertEqual(199, star1.r)
        self.assertEqual(19, star1.row)
        self.assertEqual(28, star1.col)

    def testParseEzevrtlad(self) -> None:
        sector = Sector('# Zhdant', '# -7, 2')
        star1 = Star.parse_line_into_star(
            "2820 Ezevrtlad            C120000-B De Ba Po                            - -  - 900   Zh K2 III                      ",
            sector, 'fixed', 'fixed')

        self.assertEqual(-197, star1.x)
        self.assertEqual(-1, star1.y)
        self.assertEqual(198, star1.z)
        self.assertEqual(-197, star1.q)
        self.assertEqual(198, star1.r)
        self.assertEqual(20, star1.row)
        self.assertEqual(28, star1.col)

    def testParseUnchin(self) -> None:
        sector = Sector('# Zarushagar', '# -1, -1')
        line = '0522 Unchin               A437743-E                            { 2 }  (B6D-1) [492B] B     N  - 620 9  ImDi K0 III                                                       '
        star1 = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)

    def testAPortModifier(self) -> None:
        # cwtn =[3,4,4,5,6,7,7,8,9,10,10,11,12,13,14,15]
        cwtn = [3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn * 3 + 13) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testBPortModifier(self) -> None:
        # cwtn =[2,3,4,5,5,6,7,8,8,9,10,11,11,12,12,13]
        cwtn = [2, 3, 4, 5, 5, 6, 7, 8, 8, 9, 10, 11, 11, 12, 13, 14]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn * 3 + 11) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testCPortModifier(self) -> None:
        cwtn = [2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 10, 11, 11, 12]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn + 9) // 2))) if (uwtn > 9) else int(round(max(0, (uwtn * 3 + 9) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testDPortModifier(self) -> None:
        cwtn = [1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn + 7) // 2))) if (uwtn > 7) else int(round(max(0, (uwtn * 3 + 7) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testEPortModifier(self) -> None:
        cwtn = [1, 2, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn + 5) // 2))) if (uwtn > 5) else int(round(max(0, (uwtn * 3 + 5) // 4)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testXPortModifier(self) -> None:
        # cwtn =[0,1,2,3,0,0,0,1,1,2,2,3,3,4,4,5]
        cwtn = [0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        for uwtn in range(15):
            wtn = int(round(max(0, (uwtn - 5) // 2)))
            self.assertEqual(cwtn[uwtn], wtn, "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testCalcTrade(self) -> None:
        self.assertEqual(TradeCalculation.calc_trade(0), 1)
        self.assertEqual(TradeCalculation.calc_trade(1), 5)
        self.assertEqual(TradeCalculation.calc_trade(2), 10)
        self.assertEqual(TradeCalculation.calc_trade(3), 50)
        self.assertEqual(TradeCalculation.calc_trade(4), 100)
        self.assertEqual(TradeCalculation.calc_trade(5), 500)
        self.assertEqual(TradeCalculation.calc_trade(6), 1000)

    def testPassengerBTN(self) -> None:
        self.assertEqual(TradeCalculation.calc_passengers(10), 0)
        self.assertEqual(TradeCalculation.calc_passengers(11), 5)
        self.assertEqual(TradeCalculation.calc_passengers(12), 10)
        self.assertEqual(TradeCalculation.calc_passengers(13), 50)
        self.assertEqual(TradeCalculation.calc_passengers(14), 100)
        self.assertEqual(TradeCalculation.calc_passengers(15), 500)

    def testCalcTradeTonnage(self) -> None:
        self.assertEqual(TradeCalculation.calc_trade_tonnage(0, 0), 0)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(9, 0), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(9, 49), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(9, 50), 0)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(10, 50), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(10, 99), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(10, 100), 0)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(11, 99), 5)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(11, 100), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(11, 499), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(11, 500), 0)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(12, 500), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(12, 999), 1)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(12, 1000), 0)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(13, 999), 5)
        self.assertEqual(TradeCalculation.calc_trade_tonnage(13, 1000), 1)

    def testHashValueSameAfterCaching(self) -> None:
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V  ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

        # Grabbing hash value twice, once to seed Star._hash, second to dig it out of that cache
        oldHash = star1.__hash__()
        newHash = star1.__hash__()
        self.assertEqual(oldHash, newHash)

    def testEquals(self) -> None:
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

    def testParseBespin(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        line = '0615 Bespin II            EAA19AC-4 Fl Hi He In          {+0} (98b-1) [a935] - - - 223 9  Na G1 V           '
        star1 = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsInstance(star1, Star)
        self.assertEqual('Fl He Hi In', str(star1.tradeCode))
        self.assertEqual('(98B-1)', star1.economics)
        self.assertEqual('[A935]', star1.social)

    def testStarSize(self) -> None:
        _ = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

    def test_deep_copy(self) -> None:
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

    def test_ehex_to_numeric_mapping_for_TL_A_and_up(self) -> None:
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
                    "0104 Shana Ma             E551112-" + letter + " Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

                self.assertEqual(target, star1.tl, "Unexpected mapping for TL " + letter)

    def test_document_ehex_to_numeric_mapping_for_TL_I_and_O(self) -> None:
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
                    "0104 Shana Ma             E551112-" + letter + " Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                    Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

                self.assertEqual(target, star1.tl, "Unexpected mapping for TL " + letter)

    def testCompareHexDistanceToAxialDistance(self) -> None:
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

    def test_ehex_to_int_and_back(self) -> None:
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

    def test_parse_to_line(self) -> None:
        line_list = [
            ("0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ", "K"),
            ("3030 Khaammumlar          E430761-6 De Na Po O:3032                       { -2 } (965-5) [3512] B    -  - 520 6  ImDv M0 V M5 V                                                ", "M"),
            ("1840 Mashuu               D725413-8 Ni                                    { -3 } (731-5) [1125] B    -  - 401 14 ImDv M0 V                                                     ", "M"),
            ("0101 000000000000000      ???????-?                                       { -2 } -       -      -    -  - 000 0  0000                                                          ", None),
            ("0101 000000000000000      ???????-?                                       { -2 } (731-5) [1125] -    -  - 000 0  0000                                                          ", None),
            ("0101 000000000000000      ???????-?                                       { -2 } -       [1125] -    -  - 000 0  0000                                                          ", None),
            ("0101 000000000000000      ???????-?                                       { -2 } (731-5) -      -    -  - 000 0  0000                                                          ", None),
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

    def test_parse_to_line_check_zone(self) -> None:
        line = "0101 000000000000000      ???????-?                                       { -2 } -       -      -    -    000 0  0000                                                          "
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        self.assertIsNotNone(star1)
        exp_parse = '0101 000000000000000      ???????-?                                                             -    -  - 000 0  0000                                                         '
        self.assertEqual(exp_parse, star1.parse_to_line())

    def test_parse_to_line_check_alg_code(self) -> None:
        line = "0101 000000000000000      ???????-?                                       { -2 } -       -      -    -    000 0  0000                                                          "
        star1 = Star.parse_line_into_star(line, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        self.assertIsNotNone(star1)
        star1.alg_code = ""
        self.assertEqual("", star1.alg_code)
        exp_parse = "0101 000000000000000      ???????-?                                                             -    -  - 000 0  --                                                           "
        self.assertEqual(exp_parse, star1.parse_to_line())

    def testShortSophontCodeIntoStatsCalculation(self) -> None:
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

    def testParseStarlineWithSomeUnknownUWPValues(self) -> None:
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
                self.assertFalse(star.deep_space_station)

    def testParseAnomalyWithNoDSS(self) -> None:
        line = '0618 Chandler Station          ???????-? {Anomaly}                                        -   -  - ???                       '
        sector = Sector('# Reft', '# -3,0')

        star = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsNone(star)

    def testParseAnomalyWithDSS(self) -> None:
        ParseStarInput.deep_space = {'Reft': ['0618']}
        line = '0618 Chandler Station          ???????-? {Anomaly}                                        -   -  - ???                       '
        sector = Sector('# Reft', '# -3,0')

        star = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star)
        self.assertTrue(star.deep_space_station)

    def testParseAnomalySansDSS(self) -> None:
        ParseStarInput.deep_space = {'Reft': ['0618']}
        line = '3103 Ishlagu Calibration Point ???????-? {Anomaly}                                        -   -  - ???                       '
        sector = Sector('# Reft', '# -3,0')

        star = Star.parse_line_into_star(line, sector, 'fixed', 'fixed')
        self.assertIsNone(star)

    def testParseStarlineWithoutExtensionsAndPresentUWP(self) -> None:
        sector = Sector('# Phlask', '# 3,-3')

        starline = '2618 Horden 2618          D54A367-D Ht Lo Wa O:2915                     - - - 401   So       D '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertFalse(star.oldskool, "Zero extensions present should result in oldskool")
        expected = '2618 Horden 2618          D54A367-D Ht Lo O:2915 Wa                       { -1 } -       -      -    -  - 401 0  So   D                                                       '
        actual = star.parse_to_line()
        self.assertEqual(expected, actual)
        # verify parse_to_line() results cleanly reparse
        nustar = Star.parse_line_into_star(actual, sector, 'fixed', 'fixed')
        self.assertIsNotNone(nustar, "Starline should reparse cleanly")
        self.assertFalse(nustar.oldskool, "Zero extensions present should result in oldskool")
        reactual = star.parse_to_line()
        self.assertEqual(expected, reactual)

    def testParseStarlineWithoutExtensionsAndOldskoolUWP(self) -> None:
        sector = Sector('# Phlask', '# 3,-3')

        starline = '2618 Horden 2618          ?54A367-D Ht Lo Wa O:2915                     - - - 401   So       D '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertTrue(star.oldskool, "Zero extensions present should result in oldskool")
        expected = '2618 Horden 2618          ?54A367-D Ht Lo O:2915 Wa                                             -    -  - 401 0  So   D                                                       '
        actual = star.parse_to_line()
        self.assertEqual(expected, actual)
        # verify parse_to_line() results cleanly reparse
        nustar = Star.parse_line_into_star(actual, sector, 'fixed', 'fixed')
        self.assertIsNotNone(nustar, "Starline should reparse cleanly")
        self.assertTrue(nustar.oldskool, "Zero extensions present should result in oldskool")
        reactual = star.parse_to_line()
        self.assertEqual(expected, reactual)

    def testParseStarlineWithExtensionsAndOldskoolUWP(self) -> None:
        sector = Sector('# Phlask', '# 3,-3')

        starline = '0406 Abrpriabr            X7820?0-0 Ba                          {-3} (600-5) [0000] - -  - 001 11 NaXX K0 V'
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertTrue(star.oldskool, "Zero extensions present should result in oldskool")
        expected = '0406 Abrpriabr            X7820?0-0 Ba                                                          -    -  - 001 11 NaXX K0 V                                                    '
        actual = star.parse_to_line()
        self.assertEqual(expected, actual)
        # verify parse_to_line() results cleanly reparse
        nustar = Star.parse_line_into_star(actual, sector, 'fixed', 'fixed')
        self.assertIsNotNone(nustar, "Starline should reparse cleanly")
        self.assertTrue(nustar.oldskool, "Zero extensions present should result in oldskool")
        reactual = star.parse_to_line()
        self.assertEqual(expected, reactual)

    def testParseStarlineWithAllDashExtensions(self) -> None:
        sector = Sector('# Phlask', '# 3,-3')

        starline = '2618 Horden 2618          D54A367-D Ht Lo Wa O:2915       - - -         - - - 401   So       D '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertFalse(star.oldskool, "Zero extensions present should not result in oldskool")

    def testParseStarKilongSector0104AsKkree(self) -> None:
        sector = Sector('# Kilong', '# 6,0')

        starline = '0104 Ombia                B2424QK-D Ni Po                      { 1 }  (C34+1) [455D] - K - 314 15 Kk G3 V               '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertEqual('B2424QK-D', str(star.uwp))

    def testParseStarKilongSector0104AsKkreeOutpost(self) -> None:
        sector = Sector('# Kilong', '# 6,0')

        starline = '0104 Ombia                B2424QK-D Ni Po                      { 1 }  (C34+1) [455D] - K - 314 15 KO G3 V               '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertEqual('B2424QK-D', str(star.uwp))

    def testParseStarKilongSector0104AsNonKkree(self) -> None:
        sector = Sector('# Kilong', '# 6,0')

        starline = '0104 Ombia                B2424QK-D Ni Po                      { 1 }  (C34+1) [455D] - K - 314 15 Im G3 V               '
        star = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        self.assertIsNotNone(star, "Starline should parse cleanly")
        self.assertEqual('B2424QJ-D', str(star.uwp))

    def test_eq(self) -> None:
        sector = Sector('# Kilong', '# 6,0')
        star = Star()
        star.sector = sector
        rhubarb = object()
        star._hash = rhubarb.__hash__()

        self.assertFalse(star.__eq__(rhubarb))

    def test_calculate_gwp_1(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Ri In Ag         { 0 }  (E69+0) [4726] B     - - 623 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        self.assertFalse(star1.tradeCode.low_per_capita_gwp)

        star1.calculate_gwp('fixed')
        self.assertEqual(60, star1.population)
        self.assertEqual(9838, star1.perCapita)
        self.assertEqual(590, star1.gwp)
        self.assertEqual('6', star1.uwpCodes['Pop Code'])
        del star1.uwpCodes['Pop Code']

        star1.calculate_gwp('scaled')
        self.assertEqual(36, star1.population)
        self.assertEqual(9838, star1.perCapita)
        self.assertEqual(354, star1.gwp)
        self.assertEqual('3', star1.uwpCodes['Pop Code'])
        del star1.uwpCodes['Pop Code']

        star1.calculate_gwp('benford')
        self.assertEqual(36, star1.population)
        self.assertEqual(9838, star1.perCapita)
        self.assertEqual(354, star1.gwp)
        self.assertEqual('3.6', star1.uwpCodes['Pop Code'])

    def test_calculate_gwp_2(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-8 Ni         { 0 }  (E69+0) [4726] B     - - 623 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        star1.calculate_gwp('fixed')
        self.assertEqual(60, star1.population)
        self.assertEqual(1831, star1.perCapita)
        self.assertEqual(109, star1.gwp)

    def test_calculate_gwp_3(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-L Ni         { 0 }  (E69+0) [4726] B     - - 623 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        self.assertEqual(20, star1.tl)

        star1.calculate_gwp('fixed')
        self.assertEqual(60, star1.population)
        self.assertEqual(31200, star1.perCapita)
        self.assertEqual(1872, star1.gwp)

    def test_calculate_gwp_4(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4033-B Ri In         { 0 }  (E69+0) [4726] B     - - 023 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        star1.calculate_gwp('fixed')
        self.assertEqual(0, star1.population)
        self.assertEqual(0, star1.perCapita)
        self.assertEqual(0, star1.gwp)

    def test_calculate_gwp_5(self) -> None:
        cases = [
            (0, 492, 0),
            (1, 784, 0),
            (2, 1254, 1),
            (3, 1254, 1),
            (4, 1254, 1),
            (5, 2004, 2),
            (6, 2004, 2),
            (7, 3203, 3),
            (8, 5127, 5),
            (9, 8198, 8),
            ('A', 8198, 8),
            ('B', 8198, 8),
            ('C', 13126, 13),
            ('D', 13126, 13),
            ('E', 21000, 21),
            ('F', 33600, 33),
            ('G', 54656, 54),
            ('H', 54656, 54),
            ('J', 87360, 87),
            ('K', 87360, 87),
        ]

        sector = Sector('# Core', '# 0, 0')

        for tl, perCapita, gwp in cases:
            with self.subTest(tl):
                star1 = Star.parse_line_into_star(
                    f'0103 Irkigkhan            C9C4633-{str(tl)} Ri In      - (E69+0) [4726] B     - - 123 8  Im M2 V',
                    sector, 'fixed', 'fixed')
                self.assertIsNotNone(star1)

                star1.calculate_gwp('fixed')
                self.assertEqual(1, star1.population)
                self.assertEqual(perCapita, star1.perCapita)
                self.assertEqual(gwp, star1.gwp)

    def test_calculate_gwp_6(self) -> None:
        cases = [
            (0, 0, '0'),
            (1, 10, '1'),
            (2, 13, '1'),
            (3, 17, '1'),
            (4, 22, '2'),
            (5, 28, '2'),
            (6, 36, '3'),
            (7, 47, '4'),
            (8, 60, '6'),
            (9, 78, '7')
        ]

        sector = Sector('# Core', '# 0, 0')

        for popM, population, popCode in cases:
            with self.subTest(popM):
                star1 = Star.parse_line_into_star(
                    f"0103 Irkigkhan            C9C4733-B Ri In         -  (E69+0) [4726] B     - - {popM}23 8  Im M2 V",
                    sector, 'fixed', 'fixed')
                star1.calculate_gwp('scaled')
                self.assertEqual(population, star1.population)
                self.assertEqual(popCode, star1.uwpCodes['Pop Code'])

    def test_calculate_gwp_7(self) -> None:
        cases = [
            (1, 10),
            (2, 13),
            (3, 17),
            (4, 22),
            (5, 28),
            (6, 36),
        ]

        sector = Sector('# Core', '# 0, 0')

        for popM, population in cases:
            with self.subTest(popM):
                star1 = Star.parse_line_into_star(
                    f"0103 Irkigkhan            C9C4733-B Ri In         -  (E69+0) [4726] B     - - {popM}23 8  Im M2 V",
                    sector, 'fixed', 'fixed')
                star1.calculate_gwp('benford')
                self.assertEqual(population, star1.population)

    def test_calculate_gwp_8(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4833-B Ri In         { 0 }  (E69+0) [4726] B     - - 723 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        exp_population = [400, 500, 600, 700, 800, 900]
        star1.calculate_gwp('benford')
        self.assertIn(star1.population, exp_population)

    def test_calculate_tcs_1(self) -> None:
        cases = [
            (0, 900, 0, 0),
            (1, 900, 0, 0),
            (2, 900, 0, 0),
            (3, 900, 0, 0),
            (4, 900, 0, 0),
            (5, 900, 4480, 48),
            (6, 900, 8960, 108),
            (7, 900, 13440, 181),
            (8, 900, 17920, 265),
            (9, 900, 22400, 362),
            ('A', 900, 26880, 471),
            ('B', 900, 31360, 592),
            ('C', 900, 35840, 725),
            ('D', 900, 40320, 870),
            ('E', 900, 44800, 1027),
            ('F', 900, 49280, 1197),
            ('G', 900, 53760, 1378),
            ('H', 900, 62720, 1693),
            ('J', 900, 71680, 2031),
            ('K', 900, 71680, 2128),
            ('L', 900, 71680, 2225),
        ]

        sector = Sector('# Core', '# 0, 0')
        for tl, ship_capacity, tcs_gwp, budget in cases:
            with self.subTest(tl):
                star1 = Star.parse_line_into_star(
                    f'0103 Irkigkhan            C9C4633-{str(tl)} Ri In      - (E69+0) [4726] B     - - 123 8  Im M2 V',
                    sector, 'fixed', 'fixed')
                self.assertIsNotNone(star1)

                star1.calculate_gwp('benford')
                star1.calculate_TCS()
                self.assertEqual(ship_capacity, star1.ship_capacity)
                self.assertEqual(tcs_gwp, star1.tcs_gwp)
                self.assertEqual(budget, star1.budget)

    def test_calculate_tcs_2(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4833-B Ag Po         { 0 }  (E69+0) [4726] B     - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        self.assertIsNotNone(star1)

        star1.calculate_gwp('benford')
        self.assertEqual(220, star1.population)
        star1.calculate_TCS()
        self.assertEqual(198000, star1.ship_capacity)
        self.assertEqual(2956800, star1.tcs_gwp)
        self.assertEqual(59874, star1.budget)

    def test_wilderness_refuel_1(self) -> None:
        star = Star()
        star.uwpCodes = {'Hydrographics': 'X', 'Atmosphere': '9'}
        self.assertFalse(star.wilderness_refuel())

    def test_wilderness_refuel_2(self) -> None:
        star = Star()
        star.uwpCodes = {'Hydrographics': 'A', 'Atmosphere': 'A'}
        self.assertFalse(star.wilderness_refuel())

    def test_wilderness_refuel_3(self) -> None:
        star = Star()
        star.uwpCodes = {'Hydrographics': 'A', 'Atmosphere': 'X'}
        self.assertTrue(star.wilderness_refuel())

    def test_calculate_mspr_1(self) -> None:
        star = Star()
        star.uwp = UWP('X563000-0')
        star.calculate_mspr()
        self.assertEqual(9, star.mspr)

    def test_calculate_mspr_2(self) -> None:
        cases = [
            ('X14A000-0', 4),
            ('X252000-0', 6),
            ('X370000-0', 5),
            ('X481000-0', 6),
            ('X489000-0', 7),
            ('X000000-0', 0),
            ('X095000-0', 5),
            ('X?1?000-0', 0),
            ('X?2?000-0', 0),
            ('X?3?000-0', 0),
            ('X?A?000-0', 0),
            ('X?B?000-0', 0),
            ('X?C?000-0', 0)
        ]

        for uwp, mspr in cases:
            with self.subTest(uwp):
                star = Star()
                star.uwp = UWP(uwp)
                star.calculate_mspr()
                self.assertEqual(mspr, star.mspr)

    def test_calculate_wtn_1(self) -> None:
        cases = [
            ('A000B00-F', 13),
            ('A000900-F', 12),
            ('A000900-0', 9),
            ('B000B00-F', 13),
            ('B000900-F', 11),
            ('B000900-9', 11),
            ('B000900-5', 10),
            ('C000C00-F', 12),
            ('C000B00-F', 11),
            ('C000A00-F', 11),
            ('C000900-F', 10),
            ('C000900-9', 10),
            ('C000800-9', 9),
            ('C000900-5', 9),
            ('C000900-4', 9),
            ('C000800-4', 8),
            ('C000700-4', 7),
            ('C000600-4', 6),
            ('C000500-4', 6),
            ('C000400-4', 5),
            ('C000300-4', 4),
            ('C000200-4', 3),
            ('D000900-E', 9),
            ('D000900-9', 9),
            ('D000800-9', 8),
            ('D000700-4', 7),
            ('D000600-4', 6),
            ('D000500-4', 5),
            ('D000400-4', 4),
            ('D000300-4', 4),
            ('D000200-4', 3),
            ('D000600-0', 5),
            ('E000900-9', 8),
            ('E000900-8', 7),
            ('E000700-5', 6),
            ('E000600-4', 5),
            ('E000400-4', 4),
            ('E000300-4', 3),
            ('E000200-4', 2),
            ('E000100-4', 2),
            ('X000900-0', 1),
            ('X000900-9', 3),
            ('X000100-0', 0),
        ]

        for uwp, wtn in cases:
            with self.subTest(uwp):
                star = Star()
                star.uwp = UWP(uwp)
                star.calculate_wtn()
                self.assertEqual(wtn, star.wtn)

    def test_fix_ex(self) -> None:
        cases = [
            ('E000400-4', 'Ba', '(221+2)', '(230+0)'),
            ('E000400-9', 'Ba', '(F22+2)', '(E30+0)'),
            ('E000300-4', 'Lo', '(F20+2)', '(C21+2)'),
            ('E000500-9', 'Ni', '(F20+2)', '(E40+2)'),
            ('E000400-9', 'Ni', '(F20+2)', '(E30+2)'),
            ('E000400-9', 'Ni', '(F28+2)', '(E37+2)'),
            ('E000700-9', '', '(F2F+2)', '(E6D+2)'),
        ]
        for uwp, tradecode, econ, exp_econ in cases:
            with self.subTest(uwp + " " + tradecode + " " + econ):
                star = Star()
                star.importance = 1
                star.ggCount = 1
                star.belts = 1
                star.uwp = UWP(uwp)
                star.tradeCode = TradeCodes(tradecode)
                star.economics = econ
                star.fix_ex()
                self.assertEqual(exp_econ, star.economics)

    def test_fix_cx(self) -> None:
        cases = [
            ('X000000-0', 'Ba', '[1111]', '[0000]'),
            ('E000400-4', 'Ba', '[1111]', '[1511]'),
            ('E000400-9', 'Ba', '[F222]', '[9524]'),
            ('E000300-4', 'Lo', '[F202]', '[8412]'),
            ('E000500-9', 'Ni', '[F202]', '[A614]'),
            ('E000400-9', 'Ni', '[F202]', '[9514]'),
            ('E000400-9', 'Ni', '[F282]', '[9584]'),
            ('E000700-9', '', '[F2F2]', '[C8A4]'),
            ('E000700-9', '', '[F2B2]', '[C8A4]'),
            ('E000900-9', '', '[32B2]', '[4AA4]'),
            ('E000900-9', '', '[0000]', '[4A14]'),
        ]
        for uwp, tradecode, social, exp_social in cases:
            with self.subTest(uwp + " " + tradecode + " " + social):
                star = Star()
                star.importance = 1
                star.ggCount = 1
                star.belts = 1
                star.uwp = UWP(uwp)
                star.tradeCode = TradeCodes(tradecode)
                star.social = social
                star.fix_cx()
                self.assertEqual(exp_social, star.social)

    def test_fix_tl(self) -> None:
        cases = [
            ('X000000-0', 'Ba', 1),
            ('X000000-?', '', 0)
        ]

        for uwp, tradecode, exp_tl in cases:
            with self.subTest(uwp + " " + tradecode):
                star = Star()
                star.uwp = UWP(uwp)
                star.tradeCode = TradeCodes(tradecode)
                star.fix_tl()
                self.assertEqual(exp_tl, star.tl)

    def test_calculate_ru(self) -> None:
        cases = [
            (None, 0, 'X000000-0', 'negative'),
            ('(000+0)', 0, 'X000000-0', 'negative'),
            ('(000+0)', 1, 'X000600-0', 'negative'),
            ('(111+1)', 1, 'X000600-0', 'negative'),
            ('(222-1)', -8, 'X000600-0', 'negative'),
            ('(222-1)', 7, 'X000600-0', 'scaled'),
            ('(222-2)', 6, 'X000600-0', 'scaled'),
            ('(222+0)', 8, 'X000600-0', 'scaled'),
            ('(222+2)', 16, 'X000600-0', 'scaled'),
            ('(22-22)', 8, 'X000600-0', 'scaled'),
            ('(22-222', 88, 'X000600-0', 'scaled'),
            ('(22G+2)', 128, 'X000600-0', 'scaled'),
            ('(22H+2)', 136, 'X000600-0', 'scaled'),
            ('(22J+2)', 136, 'X000600-0', 'scaled'),
            ('(22K+2)', 144, 'X000600-0', 'scaled'),
            ('(22L+2)', 152, 'X000600-0', 'scaled'),
            ('(G22+2)', 128, 'X000600-0', 'scaled'),
            ('(H22+2)', 136, 'X000600-0', 'scaled'),
            ('(J22+2)', 136, 'X000600-0', 'scaled'),
            ('(K22+2)', 144, 'X000600-0', 'scaled'),
            ('(L22+2)', 152, 'X000600-0', 'scaled'),
        ]

        for economics, exp_ru, uwp, calc in cases:
            with self.subTest(str(economics) + " " + str(exp_ru)):
                star = Star()
                star.uwp = UWP(uwp)
                star.economics = economics
                star.calculate_ru(calc)
                self.assertEqual(exp_ru, star.ru)

    def test_calculate_ru_check_log(self) -> None:
        star = Star()
        star.uwp = UWP('X000000-0')
        star.economics = '(000+0)'

        outer_logger = logging.getLogger('PyRoute.Star')
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

        exp_logs = [
            'DEBUG:PyRoute.Star:Dummy log entry to shut assertion up now that canonicalisation has been straightened out',
            'DEBUG:PyRoute.Star:RU = 1 * 0 * 1 * 1 = 0'
        ]

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            outer_logger.debug(
                'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
            )
            star.calculate_ru('negative')
            output = copy.deepcopy(outer_logs.output)
            self.assertEqual(exp_logs, output)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

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

from PyRoute.Calculation.TradeCalculation import TradeCalculation

sys.path.append('../PyRoute')
from Star import Star
from Galaxy import Sector, Galaxy


class TestStar(unittest.TestCase):

    def setUp(self):
        pass

    def testParseIrkigkhan(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual('0103', star1.position)
        self.assertTrue(star1.q == 0 and star1.r == 2, "%s, %s" % (star1.q, star1.r))
        self.assertEqual('Irkigkhan', star1.name)
        self.assertEqual('C9C4733-9', star1.uwp)
        self.assertEqual('Im', star1.alg_code)
        self.assertEqual(10, star1.population, "Population %s" % star1.population)
        self.assertEqual(9, star1.wtn, "wtn %s" % star1.wtn)
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertFalse(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertEqual(3, star1.ggCount)
        self.assertEqual(star1.star_list, ['M2 V'])

    def testParseIrkigkhanRUCollapse(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseIrkigkhanRUScaled(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseShanaMa(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual('0104', star1.position)
        self.assertTrue(star1.q == 0 and star1.r == 3, "%s, %s" % (star1.q, star1.r))
        self.assertEqual('Shana Ma', star1.name)
        self.assertEqual('E551112-7', star1.uwp)
        self.assertEqual('Im', star1.alg_code)
        self.assertEqual(0, star1.population, "Population %s" % star1.population)
        self.assertEqual(2, star1.wtn, "wtn %s" % star1.wtn)
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertTrue(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertEqual(3, star1.ggCount)
        self.assertEqual(2, len(star1.star_list))
        self.assertEqual(['K2 IV', 'M7 V'], star1.star_list)

    def testParseSyss(self):
        sector = Sector(' Core', ' 0, 0')
        star1 = Star.parse_line_into_star(
            "2323 Syss                 C400746-8 Na Va Pi                   { -1 } (A67-2) [6647] BD   S  - 510 5  ImDv M9 III D M5 V",
            sector, 'fixed', 'fixed')

        self.assertEqual('Core', star1.sector.name, star1.sector.name)
        self.assertEqual(star1.position, '2323')
        self.assertEqual(star1.name, 'Syss')
        self.assertEqual(star1.uwp, 'C400746-8')
        self.assertEqual(star1.stars, 'M9 III D M5 V')
        self.assertEqual(star1.star_list, ['M9 III', 'D', 'M5 V'])

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
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

        # Grabbing hash value twice, once to seed Star._hash, second to dig it out of that cache
        oldHash = star1.__hash__()
        newHash = star1.__hash__()
        self.assertEqual(oldHash, newHash)

    def testEquals(self):
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        star3 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

        self.assertEqual(star1, star2)
        self.assertNotEqual(star1, star3)
        self.assertNotEqual(star2, star3)


    def testStarSize(self):
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

    def test_deep_copy(self):
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        star1.index = 11
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
                    Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

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
                    Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

                self.assertEqual(target, star1.tl, "Unexpected mapping for TL " + letter)

    def test_compare_timing(self):
        star1 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        star1.index = 11
        star2 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        star2.index = 12

        num_rounds = 50000

        # object comparison
        foo = time.monotonic_ns()
        for i in range(num_rounds):
            result = star1 == star2
        for i in range(num_rounds):
            result = star1 == star1
        bar = time.monotonic_ns()

        object_time = bar - foo

        # property comparison
        foo = time.monotonic_ns()
        for i in range(num_rounds):
            result = star1.index == star2.index
        for i in range(num_rounds):
            result = star1.index == star1.index
        bar = time.monotonic_ns()

        property_time = bar - foo

        # saved index comparison
        ind1 = star1.index
        ind2 = star2.index

        foo = time.monotonic_ns()
        for i in range(num_rounds):
            result = ind1 == ind2
        for i in range(num_rounds):
            result = ind1 == ind1
        bar = time.monotonic_ns()

        saved_time = bar - foo
        prop_ratio = property_time / saved_time
        obj_ratio = object_time / saved_time

        self.assertTrue(object_time > saved_time, "Object comparison unexpectedly faster than integer comparison")
        self.assertTrue(property_time > saved_time, "Property comparison unexpectedly faster than integer comparison")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

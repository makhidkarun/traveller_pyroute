'''
Created on Mar 7, 2014

@author: tjoneslo
'''
import unittest
import re
import sys
sys.path.append('../PyRoute')
from Star import Star
from Galaxy import Sector,Galaxy
from TradeCalculation import TradeCalculation


class TestStar(unittest.TestCase):

    def setUp(self):

        star_regex = ''.join([line.rstrip('\n') for line in Galaxy.regex])
        self.starline = re.compile(star_regex)

    def testParseIrkigkhan(self):
        sector = Sector('Core', ' 0, 0')
        star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, sector, 'fixed',  None)

        self.assertTrue(star1.sector.name == 'Core', star1.sector.name)
        self.assertTrue(star1.position == '0103')
        self.assertTrue(star1.q == 0 and star1.r == 2, "%s, %s" % (star1.q, star1.r))
        self.assertTrue(star1.name == 'Irkigkhan')
        self.assertTrue(star1.uwp == 'C9C4733-9')
        self.assertTrue(star1.alg == 'Im')
        self.assertTrue(star1.population == 10, "Population %s" % star1.population)
        self.assertTrue(star1.wtn == 9, "wtn %s" % star1.wtn)
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertFalse(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertTrue(star1.ggCount == 3)
        self.assertEqual(star1.star_list, ['M2 V'])

    def testParseIrkigkhanRUCollapse(self):
        sector = Sector('Core', ' 0, 0')
        star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, sector, 'fixed',  'collapse')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseIrkigkhanRUScaled(self):
        sector = Sector('Core', ' 0, 0')
        star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, sector, 'fixed',  'scaled')

        expected = 756
        actual = star1.ru

        self.assertEqual(expected, actual)

    def testParseShanaMa(self):
        sector = Sector('Core', ' 0, 0')
        star1 = Star.parse_line_into_star("0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                     self.starline,  sector, 'fixed',  None)

        self.assertTrue(star1.sector.name == 'Core', star1.sector.name)
        self.assertTrue(star1.position == '0104')
        self.assertTrue(star1.q == 0 and star1.r == 3, "%s, %s" % (star1.q, star1.r))
        self.assertTrue(star1.name == 'Shana Ma')
        self.assertTrue(star1.uwp == 'E551112-7')
        self.assertTrue(star1.alg == 'Im')
        self.assertTrue(star1.population == 0, "Population %s" % star1.population)
        self.assertTrue(star1.wtn == 2, "wtn %s" % star1.wtn)
        self.assertFalse(star1.tradeCode.industrial)
        self.assertFalse(star1.tradeCode.agricultural)
        self.assertTrue(star1.tradeCode.poor)
        self.assertFalse(star1.tradeCode.rich)
        self.assertTrue(star1.ggCount == 3)
        self.assertEqual(len(star1.star_list), 2)
        self.assertEqual(star1.star_list, ['K2 IV', 'M7 V'])
        
    def testParseSyss(self):
        sector = Sector('Core', ' 0, 0')
        star1 = Star.parse_line_into_star("2323 Syss                 C400746-8 Na Va Pi                   { -1 } (A67-2) [6647] BD   S  - 510 5  ImDv M9 III D M5 V",
                     self.starline, sector, 'fixed',  None)

        self.assertTrue(star1.sector.name == 'Core', star1.sector.name)
        self.assertEqual(star1.position, '2323')
        self.assertEqual(star1.name, 'Syss')
        self.assertEqual(star1.uwp, 'C400746-8')
        self.assertEqual(star1.stars, 'M9 III D M5 V')
        self.assertEqual(star1.star_list, ['M9 III', 'D', 'M5 V'])

    def testAPortModifier(self):
        #cwtn =[3,4,4,5,6,7,7,8,9,10,10,11,12,13,14,15]
        cwtn = [3,4,4,5,6,7,7,8,9,10,10,11,12,13,13,14]
        for uwtn in xrange(15):
            wtn = int(round(max(0, (uwtn * 3 + 13) / 4)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testBPortModifier(self):
        #cwtn =[2,3,4,5,5,6,7,8,8,9,10,11,11,12,12,13]
        cwtn = [2,3,4,5,5,6,7,8,8,9,10,11,11,12,13,14]
        for uwtn in xrange(15):
            wtn = int(round(max(0, (uwtn * 3 + 11) / 4)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testCPortModifier(self):
        cwtn = [2,3,3,4,5,6,6,7,8,9,9,10,10,11,11,12]
        for uwtn in xrange(15):
            if (uwtn > 9):
                wtn = int(round(max(0, (uwtn + 9)/2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 9)/4)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testDPortModifier(self):
        cwtn = [1,2,3,4,4,5,6,7,7,8,8,9,9,10,10,11]
        for uwtn in xrange(15):        
            if (uwtn > 7):
                wtn =int(round(max(0, (uwtn + 7) / 2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 7) / 4)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testEPortModifier(self):
        cwtn = [1,2,2,3,4,5,5,6,6,7,7,8,8,9,9,10]
        for uwtn in xrange(15):        
            if (uwtn > 5):
                wtn =int(round(max(0, (uwtn + 5) / 2)))
            else:
                wtn = int(round(max(0, (uwtn * 3 + 5) / 4)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

    def testXPortModifier(self):
        #cwtn =[0,1,2,3,0,0,0,1,1,2,2,3,3,4,4,5]
        cwtn = [0,0,0,0,0,0,0,1,1,2,2,3,3,4,4,5]
        for uwtn in xrange(15):
            wtn = int(round(max(0, (uwtn - 5) / 2)))
            self.assertTrue (wtn == cwtn[uwtn], "at %s: %s vs %s" % (uwtn, wtn, cwtn[uwtn]))

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
        star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V  ",
             self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
    
        # Grabbing hash value twice, once to seed Star._hash, second to dig it out of that cache
        oldHash = star1.__hash__()
        newHash = star1.__hash__()
        self.assertEqual(oldHash,  newHash)

    def TestEquals(self):
        star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
             self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
        star2 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
             self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
        star3 = Star.parse_line_into_star("0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                     self.starline,  Sector('Core', ' 0, 0'), 'fixed',  None)
        
        self.assertEqual(star1,  star2)
        self.assertNotEqual(star1,  star3)
        self.assertNotEqual(star2,  star3)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

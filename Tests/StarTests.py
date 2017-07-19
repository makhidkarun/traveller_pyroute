'''
Created on Mar 7, 2014

@author: tjoneslo
'''
import unittest
import re
import sys
sys.path.append('../PyRoute')
from Star import Star
from Galaxy import Sector
from TradeCalculation import TradeCalculation

class Test(unittest.TestCase):

    def setUp(self):
        regex =  """
^(\d\d\d\d) +
(.{15,}) +
(\w\w\w\w\w\w\w-\w) +
(.{15,}) +
((\{ [+-]?[0-5] \}) +(\([0-9A-Z]{3}[+-]\d\)) +(\[[0-9A-Z]{4}\])|( ) ( ) ( )) +
(\w{1,5}|-) +
(\w\w?|-|\*) +
(\w|-) +
([0-9][0-9A-F][0-9A-F]) +
(\d{1,}| )+
([A-Z0-9-][A-Za-z0-9-]{1,3}) 
(.*)
"""

        star_regex = ''.join([line.rstrip('\n') for line in regex])
        self.starline = re.compile(star_regex)

    def testParseIrkigkhan(self):
        star1 = Star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
        
        self.assertTrue(star1.position == '0103')
        self.assertTrue(star1.q == 0 and star1.r == 2, "%s, %s" % (star1.q, star1.r))
        self.assertTrue(star1.name == 'Irkigkhan')
        self.assertTrue(star1.uwp == 'C9C4733-9')
        self.assertTrue(star1.alg == 'Im')
        self.assertTrue(star1.population == 10, "Population %s" % star1.population)
        self.assertTrue(star1.wtn == 9, "wtn %s" % star1.wtn)
        self.assertFalse(star1.industrial)
        self.assertFalse(star1.agricultural)
        self.assertFalse(star1.poor)
        self.assertFalse(star1.rich)
        self.assertTrue(star1.ggCount == 3)

    def testParseShanaMa(self):
        star1 = Star("0104 Shana Ma             E551112-7 Lo Po                { -3 } (300-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                     self.starline,  Sector('Core', ' 0, 0'), 'fixed',  None)
        self.assertTrue(star1.position == '0104')
        self.assertTrue(star1.q == 0 and star1.r == 3, "%s, %s" % (star1.q, star1.r))
        self.assertTrue(star1.name == 'Shana Ma')
        self.assertTrue(star1.uwp == 'E551112-7')
        self.assertTrue(star1.alg == 'Im')
        self.assertTrue(star1.population == 0, "Population %s" % star1.population)
        self.assertTrue(star1.wtn == 2, "wtn %s" % star1.wtn)
        self.assertFalse(star1.industrial)
        self.assertFalse(star1.agricultural)
        self.assertTrue(star1.poor)
        self.assertFalse(star1.rich)
        self.assertTrue(star1.ggCount == 3)
        
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



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

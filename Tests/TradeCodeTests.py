import unittest
import sys
import re
import logging
sys.path.append('../PyRoute')
from TradeCodes import TradeCodes
from Star import Star
from Galaxy import Sector

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
        self.star1 = Star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
        self.star2 = Star("0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
                     self.starline,  Sector('Core', ' 0, 0'), 'fixed',  None)
        
        self.logger = logging.getLogger("PyRoute")
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel("INFO")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        
    def testLo(self):
        code = TradeCodes("Lo")
        self.assertTrue(code.pcode is None)
        self.assertTrue(str(code) == u'Lo')
        self.assertTrue(code.low)
        self.assertFalse(code.high)

    def testOrdering(self):
        code = TradeCodes("Wa Ag Ni")
        self.assertTrue(code.pcode == 'Wa')
        self.assertTrue(str(code) == u'Ag Ni Wa')
        self.assertTrue(code.agricultural)
        self.assertTrue(code.nonindustrial)
    
    def testColony(self):
        code = TradeCodes(u"Ph C:0404")
        self.assertTrue(code.owned == [u'C:0404'], code.owned)
        self.assertTrue(code.colonies("Spinward Marches") == [u'C:Spin-0404'], code.colonies("Spinward Marches"))
        self.assertTrue(code.owners('Spinward Marvhes') == [])
        
    def testOwned (self):
        code = TradeCodes(u"Ag O:1011")
        self.assertTrue(code.owned == [u'O:1011'], code.owned)
        self.assertTrue(code.owners('Deneb') == [u'O:Dene-1011'])
        self.assertTrue(code.colonies('Deneb') == [])
        
    def testSophonts(self):
        code = TradeCodes(u"(Wiki)")
        self.assertTrue(code.homeworld)
        self.assertTrue(code.homeworlds == [u'(Wiki)'], code.homeworlds)
        self.assertTrue(code.sophonts == [u'Wiki'])
        
    def testWorldSophont(self):
        code = TradeCodes("Ag Huma4")
        self.assertFalse(code.homeworld)
        self.assertTrue(code.homeworlds == ['Huma4'])
        self.assertTrue(code.sophonts == [])
        
    def testSophontCompbined(self):
        code = TradeCodes("Ri (Wiki) Huma4 Wiki2 (Deneb)")
        self.assertTrue(code.homeworld)
        self.assertTrue(code.sophonts == ['Wiki', 'Deneb'])
        self.assertTrue(code.homeworlds == ['Huma4', '(Deneb)', '(Wiki)', 'Wiki2'], code.homeworlds)
        
    def testCodeCheck(self):
        code = TradeCodes("Fl")
        self.assertTrue(code.check_world_codes(self.star1))
        
    def testCodeCheck2(self):
        code = TradeCodes("Po Lo")
        self.assertTrue(code.check_world_codes(self.star2))
        self.assertTrue(code.poor)
        self.assertTrue(code.low)
        
    def testCodeCheckFails(self):
        code = TradeCodes("Wa")
        self.assertFalse(code.check_world_codes(self.star1))
        self.assertFalse(code.check_world_codes(self.star2))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

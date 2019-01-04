import unittest     
import sys
import re
import logging
sys.path.append('../PyRoute')
from TradeCodes import TradeCodes
from Star import Star
from Galaxy import Sector, Galaxy


class TestTradeCode(unittest.TestCase):

    def setUp(self):
        star_regex = ''.join([line.rstrip('\n') for line in Galaxy.regex])

        self.starline = re.compile(star_regex)
        self.star1 = Star.parse_line_into_star("0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
                     self.starline, Sector('Core', ' 0, 0'), 'fixed',  None)
        self.star2 = Star.parse_line_into_star("0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
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
        self.assertTrue(code.owners('Spinward Marches') == [])
        
    def testOwned (self):
        code = TradeCodes(u"Ag O:1011")
        self.assertTrue(code.owned == [u'O:1011'], code.owned)
        self.assertTrue(code.owners('Deneb') == [u'O:Dene-1011'])
        self.assertTrue(code.colonies('Deneb') == [])
        
    def testSophonts(self):
        code = TradeCodes(u"(Wiki)")
        self.assertTrue(code.homeworld == [u'Wiki'], code.homeworld)
        self.assertTrue(code.sophonts == [u'WikiW'], code.sophonts)
        
    def testSophontsPartial(self):
        code = TradeCodes(u"(Wiki)4")
        self.assertTrue(code.homeworld == [u'Wiki'], code.homeworld)
        self.assertTrue(code.sophonts == [u'Wiki4'])

    def testWorldSophont(self):
        code = TradeCodes("Ag Huma4")
        self.assertFalse(code.homeworld)
        self.assertTrue(code.sophonts == ['Huma4'])
        self.assertTrue(code.codeset == ['Ag'])
        
    def testWorldSophontsMultiple(self):
        code = TradeCodes("Ag Wiki4 Huma2")
        self.assertFalse(code.homeworld)
        self.assertTrue(code.sophonts == ['Wiki4', 'Huma2'])
        self.assertTrue(code.codeset == ['Ag'])
        
    def testSophontCombined(self):
        code = TradeCodes("Ri (Wiki) Huma4 Alph2 (Deneb)2")
        self.assertTrue(len(code.homeworld) > 0)
        self.assertTrue(code.sophonts == ['Huma4', 'Alph2', 'WikiW', 'Dene2'], msg=code.sophonts)
        self.assertTrue(code.homeworld == ['Wiki', 'Deneb'], msg=code.homeworld)
        self.assertTrue(code.codeset == ['Ri'], code.codeset)
        
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

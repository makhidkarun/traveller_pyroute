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
        self.star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')
        self.star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector(' Core', ' 0, 0'), 'fixed', 'fixed')

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
        self.assertEqual(u'Lo', str(code))
        self.assertTrue(code.low)
        self.assertFalse(code.high)

    def testOrdering(self):
        code = TradeCodes("Wa Ag Ni")
        self.assertEqual('Wa', code.pcode)
        self.assertEqual(u'Ag Ni Wa', str(code))
        self.assertTrue(code.agricultural)
        self.assertTrue(code.nonindustrial)

    def testColony(self):
        code = TradeCodes(u"Ph C:0404")
        self.assertEqual([u'C:0404'], code.owned, code.owned)
        self.assertEqual([u'C:Spin-0404'], code.colonies("Spinward Marches"), code.colonies("Spinward Marches"))
        self.assertEqual([], code.owners('Spinward Marches'))

    def testOwned(self):
        code = TradeCodes(u"Ag O:1011")
        self.assertEqual([u'O:1011'], code.owned, code.owned)
        self.assertEqual([u'O:Dene-1011'], code.owners('Deneb'))
        self.assertEqual([], code.colonies('Deneb'))

    def testSophonts(self):
        code = TradeCodes(u"(Wiki)")
        self.assertEqual([u'WikiW'], code.homeworld, code.homeworld)
        self.assertEqual([u'WikiW'], code.sophonts, code.sophonts)

    def testSophontsPartial(self):
        code = TradeCodes(u"(Wiki)4")
        self.assertEqual([u'Wiki4'], code.homeworld, code.homeworld)
        self.assertEqual([u'Wiki4'], code.sophonts)

    def testWorldSophont(self):
        code = TradeCodes("Ag Huma4")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Huma4'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testWorldSophontsMultiple(self):
        code = TradeCodes("Ag Wiki4 Huma2")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Wiki4', 'Huma2'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testSophontCombined(self):
        code = TradeCodes("Ri (Wiki) Huma4 Alph2 (Deneb)2")
        self.assertTrue(len(code.homeworld) > 0)
        self.assertEqual(['Huma4', 'Alph2', 'WikiW', 'Dene2'], code.sophonts, msg=code.sophonts)
        self.assertEqual(['WikiW', 'Dene2'], code.homeworld, msg=code.homeworld)
        self.assertEqual(['Ri'], code.codeset, code.codeset)

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
        with self.assertLogs(self.logger, level='ERROR') as log:
            self.assertFalse(code.check_world_codes(self.star1))
            # assert that what we expected was logged
            self.assertEqual(2, len(log.output))
            self.assertEqual(
                [
                    'ERROR:PyRoute.TradeCodes:Irkigkhan (Core 0103)-C9C4733-9 Calculated "Fl" not in trade codes [\'Wa\']',
                    'ERROR:PyRoute.TradeCodes:Irkigkhan (Core 0103)-C9C4733-9 Found invalid "Wa" in trade codes: [\'Wa\']'
                ],
                log.output)
        with self.assertLogs(self.logger, level='ERROR') as log:
            self.assertFalse(code.check_world_codes(self.star2))
            # assert that what we expected was logged
            self.assertEqual(3, len(log.output))
            self.assertEqual(
                [
                    'ERROR:PyRoute.TradeCodes:Shana Ma (Core 0104)-E551112-7 Calculated "Po" not in trade codes [\'Wa\']',
                    'ERROR:PyRoute.TradeCodes:Shana Ma (Core 0104)-E551112-7 Found invalid "Wa" in trade codes: [\'Wa\']',
                    'ERROR:PyRoute.TradeCodes:Shana Ma (Core 0104) - Calculated "Lo" not in trade codes [\'Wa\']',
                ],
                log.output
            )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

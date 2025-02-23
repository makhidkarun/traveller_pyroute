import unittest
import sys
import logging

sys.path.append('../PyRoute')
from PyRoute.AreaItems.Sector import Sector
from PyRoute.TradeCodes import TradeCodes
from PyRoute.Star import Star


class TestTradeCode(unittest.TestCase):

    def setUp(self):
        self.star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
        self.star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            Sector('# Core', '# 0, 0'), 'fixed', 'fixed')

        self.logger = logging.getLogger("PyRoute")

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logging.disable(logging.NOTSET)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel("INFO")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        logger = logging.getLogger('PyRoute.TradeCodes')
        logger.setLevel(logging.WARNING)

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
        self.assertEqual([u'Wiki'], code.homeworld, code.homeworld)
        self.assertEqual([u'WikiW'], code.sophonts, code.sophonts)

    def testSophontsPartial(self):
        code = TradeCodes(u"(Wiki)4")
        self.assertEqual([u'Wiki'], code.homeworld, code.homeworld)
        self.assertEqual([u'Wiki4'], code.sophonts)

    def testWorldSophont(self):
        code = TradeCodes("Ag Huma4")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Huma4'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testAllSophontCodesAreBelongToUs(self):
        soph_codes = ['Adda', 'Aezo', 'Akee', 'Aqua', 'Asla', 'Bhun', 'Grin', 'Gruh', 'Buru', 'Bwap', 'Chir', 'Clot',
                      'Darm', 'Dary', 'Dolp', 'Droy', 'Dync', 'Esly', 'Flor', 'Geon', 'Gnii', 'Gray', 'Guru', 'Gurv',
                      'Hama', 'Hive', 'Huma', 'Ithk', 'Jaib', 'Jala', 'Jend', 'Jonk', 'Kafo', 'Kagg', 'Karh', 'Kiak',
                      'K\'kr', 'Lamu', 'Lanc', 'Libe', 'Llel', 'Luri', 'Mal\'', 'Mask', 'Mitz', 'Muri', 'Ocra', 'Ormi',
                      'Scan', "Sele", 'S\'mr', 'Sred', 'Stal', 'Suer', 'Sull', 'Swan', 'Sydi', 'Syle', 'Tapa', 'Taur',
                      'Tent', 'Tlye', 'UApe', 'Ulan', 'Ursa', 'Urun', 'Varg', 'Vega', 'Yile', 'Za\'t', 'Zhod', 'Ziad']

        for soph in soph_codes:
            with self.subTest():
                soph += '1'
                code = TradeCodes(soph)
                self.assertEqual([soph], code.sophonts, 'Sophont code ' + soph + " not in sophont-list")
                self.assertEqual([], code.codeset, 'Codeset should be empty')

    def testWorldSophontsMultiple(self):
        code = TradeCodes("Ag Wiki4 Huma2")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Huma2', 'Wiki4'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testSophontCombined(self):
        code = TradeCodes("Ri (Wiki) Huma4 Alph2 (Deneb)2")
        self.assertTrue(len(code.homeworld) > 0)
        self.assertEqual(['Alph2', 'Dene2', 'Huma4', 'WikiW'], code.sophonts, msg=code.sophonts)
        self.assertEqual(['Deneb', 'Wiki'], code.homeworld, msg=code.homeworld)
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
                    'ERROR:PyRoute.TradeCodes:Shana Ma (Core 0104)-E551112-7 Calculated "Lo" not in trade codes [\'Wa\']',
                ],
                log.output
            )

    def testSophontHomeworldWithSpaces(self):
        cases = [
            ('Minor race', 'Ni Pa (Ashdak Meshukiiba) Sa ', '(Ashdak Meshukiiba) Ni Pa Sa'),
            ('Major race', 'Ni Pa [Ashdak Meshukiiba] Sa ', 'Ni Pa Sa [Ashdak Meshukiiba]')
        ]

        for msg, line, expected_line in cases:
            with self.subTest(msg):
                code = TradeCodes(line)
                result, msg = code.is_well_formed()
                self.assertTrue(result, msg)
                self.assertEqual(1, len(code.sophont_list))
                self.assertEqual(1, len(code.homeworld_list))
                self.assertEqual(['AshdW'], code.sophonts, 'Unexpected sophont list')
                self.assertEqual(['Ashdak Meshukiiba'], code.homeworld_list, 'Unexpected homeworld list')
                self.assertEqual(expected_line, str(code))

    def testSophontDiebackAlongsideActivePopulations(self):
        line = 'An Asla1 Cs Hi MiyaX S\'mr0'
        code = TradeCodes(line)
        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        self.assertEqual(1, len(code.homeworld_list))
        self.assertEqual(["MiyaX"], code.homeworld_list)
        self.assertEqual(["Asla1", "S\'mr0", "MiyaX"], code.sophont_list)

    def testAvoidFakeoutHomeworldAtEnd(self):
        line = '000000000(0) 00'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldAtStart(self):
        line = '(0)000000000 00'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldInMiddle(self):
        line = '00000000000(0)0'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldWithSpace(self):
        line = '000000000000( )'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testVerifyActualHomeworld(self):
        line = '(0000)W'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in sophont")

    def testVerifyHomeworldDoesNotDuplicate(self):
        line = '(Ashd)W Ni Pa Sa'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in sophont")

        nuline = str(code)
        self.assertEqual(line, nuline)

    def testVerifyHomeworldWithUnknownPopCountsAsZero(self):
        line = 'Pi (Feime)? Re Sa'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")
        self.assertEqual(['Feim0'], code.sophont_list)
        self.assertEqual(['Feime'], code.homeworld_list)

        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        expected_line = '(Feime)? Pi Re Sa'
        self.assertEqual(expected_line, str(code), "Unexpected parsed trade code")

    def testVerifyHomeworldMinorRace(self):
        line = 'Hi In (Anixii)W Da'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")
        self.assertEqual(['AnixW'], code.sophont_list)
        self.assertEqual(['Anixii'], code.homeworld_list)

        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        expected_line = '(Anixii)W Da Hi In'
        self.assertEqual(expected_line, str(code), "Unexpected string representation")

    def testVerifyHomeworldMajorRaceImplicitPop(self):
        line = 'Hi In [Anixii] Da'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")
        self.assertEqual(['AnixW'], code.sophont_list)
        self.assertEqual(['Anixii'], code.homeworld_list)

        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        expected_line = 'Da Hi In [Anixii]'
        self.assertEqual(expected_line, str(code), "Unexpected string representation")

    def testVerifyHomeworldMajorRaceExplicitPop(self):
        line = 'Hi In [Anixii]9 Da'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")
        self.assertEqual(['Anix9'], code.sophont_list)
        self.assertEqual(['Anixii'], code.homeworld_list)

        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        expected_line = 'Da Hi In [Anixii]9'
        self.assertEqual(expected_line, str(code), "Unexpected string representation")

    def testVerifyDeadworldDoesntSpawnHomeworld(self):
        line = '(Miya)X An Asla1 Cs Hi S\'mr0'
        code = TradeCodes(line)
        self.assertEqual(3, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")

        expected = '(Miya)X An Asla1 Cs Hi S\'mr0'
        self.assertEqual(expected, str(code), "Unexpected trade code result")

    def testVerifyCompactChirperCodeProcessing(self):
        poplevel = '0123456789W'

        for rawcode in poplevel:
            with self.subTest("Population code " + rawcode):
                line = 'C' + rawcode
                code = TradeCodes(line)
                expected = 'Chir' + rawcode
                self.assertEqual(1, len(code.sophont_list), "Compacted Chirper code should result in sophont")
                self.assertEqual(expected, str(code))

    def testVerifyCompactDroyneCodeProcessing(self):
        poplevel = '0123456789W'

        for rawcode in poplevel:
            with self.subTest("Population code " + rawcode):
                line = 'D' + rawcode
                code = TradeCodes(line)
                expected = 'Droy' + rawcode
                self.assertEqual(1, len(code.sophont_list), "Compacted Droyne code should result in sophont")
                self.assertEqual(expected, str(code))

    def testSharedHomeworld(self):
        cases = [
            ('Both minor, both populations explicit', 'Hi Pz (S\'mrii)7 (Kiakh\'iee)3 ', '(Kiakh\'iee)3 (S\'mrii)7 Hi Pz', ['Kiak3', 'SXmr7']),
            ('Both major, both populations explicit', 'Hi Pz [S\'mrii]7 [Kiakh\'iee]3 ', 'Hi Pz [Kiakh\'iee]3 [S\'mrii]7', ['Kiak3', 'SXmr7']),
            ('First major, both populations explicit', 'Hi Pz [S\'mrii]7 (Kiakh\'iee)3 ', '(Kiakh\'iee)3 Hi Pz [S\'mrii]7', ['Kiak3', 'SXmr7']),
            ('Second major, both populations explicit', 'Hi Pz (S\'mrii)7 [Kiakh\'iee]3 ', '(S\'mrii)7 Hi Pz [Kiakh\'iee]3', ['Kiak3', 'SXmr7']),
            ('Second major, first population zero, second population implicit', 'Hi Pz (S\'mrii)0 [Kiakh\'iee] ', '(S\'mrii)0 Hi Pz [Kiakh\'iee]', ['KiakW', 'SXmr0']),
            ('First major, both populations zero', 'Hi Pz [S\'mrii]0 (Kiakh\'iee)0 ', '(Kiakh\'iee)0 Hi Pz [S\'mrii]0', ['Kiak0', 'SXmr0']),
            ('Second major, first population explicit, second population zero', 'Hi Pz (S\'mrii)7 [Kiakh\'iee]0 ', '(S\'mrii)7 Hi Pz [Kiakh\'iee]0', ['Kiak0', 'SXmr7']),
            ('Both minor, first population implicit, second population zero', 'Hi Pz (S\'mrii) (Kiakh\'iee)0 ', '(Kiakh\'iee)0 (S\'mrii) Hi Pz', ['Kiak0', 'SXmrW']),
            ('Both major, first population implicit, second population zero', 'Hi Pz [S\'mrii] [Kiakh\'iee]0 ', 'Hi Pz [Kiakh\'iee]0 [S\'mrii]', ['Kiak0', 'SXmrW']),
            ('First major, first population zero, second population implicit', 'Hi Pz [S\'mrii]0 (Kiakh\'iee) ', '(Kiakh\'iee) Hi Pz [S\'mrii]0', ['KiakW', 'SXmr0']),
            ('First major, first population zero, second population explicit', 'Hi Pz [S\'mrii]0 (Kiakh\'iee)3 ', '(Kiakh\'iee)3 Hi Pz [S\'mrii]0', ['Kiak3', 'SXmr0'])
        ]

        for label, line, expected_line, expected_sophont in cases:
            with self.subTest(label):
                code = TradeCodes(line)
                result, msg = code.is_well_formed()
                self.assertTrue(result, msg)

                self.assertEqual(2, len(code.sophont_list), "Shared homeworld should result in two sophont")
                self.assertEqual(2, len(code.homeworld_list), "Shared homeworld should result in two homeworld entries")

                self.assertEqual(expected_sophont, code.sophonts, "Unexpected sophont list")
                expected_homeworld = ['Kiakh\'iee', 'S\'mrii']
                self.assertEqual(expected_homeworld, code.homeworld, "Unexpected homeworld list")

                self.assertEqual(expected_line, str(code), "Unexpected string representation")

                nu_code = TradeCodes(str(code))
                result, msg = nu_code.is_well_formed()
                self.assertTrue(result, msg)

    def testHandleOverlyLongSophontName(self):
        cases = [
            ('Minor race', '(', ')'),
            ('Major race', '(', ')')
        ]

        for msg, left_bracket, right_bracket in cases:
            with self.subTest(msg):
                line = left_bracket + '000000000000000000000000000000000000' + right_bracket
                code = TradeCodes(line)
                sophont = line[1:36]  # strip the brackets and trim what's left to 35 characters

                self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
                self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")
                self.assertEqual(['0000W'], code.sophont_list)
                self.assertEqual([sophont], code.homeworld_list)

                # verify shortened soph code turns up
                expected_sophont = left_bracket + sophont + right_bracket
                nu_line = str(code)
                self.assertEqual(expected_sophont, nu_line)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

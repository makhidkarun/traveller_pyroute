import copy
import unittest
import logging

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Errors.MultipleWPopError import MultipleWPopError
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.TradeCodes import TradeCodes
from PyRoute.Star import Star
from PyRoute.SystemData.UWP import UWP


class TestTradeCode(unittest.TestCase):

    def setUp(self) -> None:
        ParseStarInput.deep_space = {}
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

    def testLo(self) -> None:
        code = TradeCodes("Lo")
        self.assertTrue(code.pcode is None)
        self.assertEqual(u'Lo', str(code))
        self.assertTrue(code.low)
        self.assertFalse(code.high)

    def testOrdering(self) -> None:
        code = TradeCodes("Wa Ag Ni")
        self.assertEqual('Wa', code.pcode)
        self.assertEqual(u'Ag Ni Wa', str(code))
        self.assertTrue(code.agricultural)
        self.assertTrue(code.nonindustrial)

    def testColony(self) -> None:
        code = TradeCodes(u"Ph C:0404")
        self.assertEqual([u'C:0404'], code.owned, code.owned)
        self.assertEqual([u'C:Spin-0404'], code.colonies("Spinward Marches"), code.colonies("Spinward Marches"))
        self.assertEqual([], code.owners('Spinward Marches'))

    def testOwned(self) -> None:
        code = TradeCodes(u"Ag O:1011")
        self.assertEqual([u'O:1011'], code.owned, code.owned)
        self.assertEqual([u'O:Dene-1011'], code.owners('Deneb'))
        self.assertEqual([], code.colonies('Deneb'))

    def testSophonts(self) -> None:
        code = TradeCodes(u"(Wiki)")
        self.assertEqual([u'Wiki'], code.homeworld, code.homeworld)
        self.assertEqual([u'WikiW'], code.sophonts, code.sophonts)

    def testSophontsPartial(self) -> None:
        code = TradeCodes(u"(Wiki)4")
        self.assertEqual([u'Wiki'], code.homeworld, code.homeworld)
        self.assertEqual([u'Wiki4'], code.sophonts)

    def testWorldSophont(self) -> None:
        code = TradeCodes("Ag Huma4")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Huma4'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testAllSophontCodesAreBelongToUs(self) -> None:
        soph_codes = ['Adda', 'Aezo', 'Akee', 'Aqua', 'Asla', 'Bhun', 'Grin', 'Gruh', 'Buru', 'Bwap', 'Chir', 'Clot',
                      'Darm', 'Dary', 'Dolp', 'Droy', 'Dync', 'Esly', 'Flor', 'Geon', 'Gnii', 'Gray', 'Guru', 'Gurv',
                      'Hama', 'Hive', 'Huma', 'Ithk', 'Jaib', 'Jala', 'Jend', 'Jonk', 'Kafo', 'Kagg', 'Karh', 'Kiak',
                      'K\'kr', 'Lamu', 'Lanc', 'Libe', 'Llel', 'Luri', 'Mal\'', 'Mask', 'Mitz', 'Muri', 'Ocra', 'Ormi',
                      'Scan', "Sele", 'S\'mr', 'Sred', 'Stal', 'Suer', 'Sull', 'Swan', 'Sydi', 'Syle', 'Tapa', 'Taur',
                      'Tent', 'Tlye', 'UApe', 'Ulan', 'Ursa', 'Urun', 'Varg', 'Vega', 'Yile', 'Za\'t', 'Zhod', 'Ziad']

        for raw_soph in soph_codes:
            with self.subTest():
                soph = raw_soph + '1'
                code = TradeCodes(soph)
                self.assertEqual([soph], code.sophonts, 'Sophont code ' + soph + " not in sophont-list")
                self.assertEqual([], code.codeset, 'Codeset should be empty')

    def testWorldSophontsMultiple(self) -> None:
        code = TradeCodes("Ag Wiki4 Huma2")
        self.assertFalse(code.homeworld)
        self.assertEqual(['Huma2', 'Wiki4'], code.sophonts)
        self.assertEqual(['Ag'], code.codeset)

    def testSophontCombined(self) -> None:
        code = TradeCodes("Ri (Wiki) Huma4 Alph2 (Deneb)2")
        self.assertTrue(len(code.homeworld) > 0)
        self.assertEqual(['Alph2', 'Dene2', 'Huma4', 'WikiW'], code.sophonts, msg=code.sophonts)
        self.assertEqual(['Deneb', 'Wiki'], code.homeworld, msg=code.homeworld)
        self.assertEqual(['Ri'], code.codeset, code.codeset)

    def testCodeCheck(self) -> None:
        code = TradeCodes("Fl")
        self.assertTrue(code.check_world_codes(self.star1))

    def testCodeCheck2(self) -> None:
        code = TradeCodes("Po Lo")
        self.assertTrue(code.check_world_codes(self.star2))
        self.assertTrue(code.poor)
        self.assertTrue(code.low)

    def testCodeCheckFails(self) -> None:
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

    def testSophontHomeworldWithSpaces(self) -> None:
        cases = [
            ('Minor race', 'Ni Pa (Ashdak Meshukiiba) Sa ', '(Ashdak Meshukiiba) Ni Pa Sa'),
            ('Major race', 'Ni Pa [Ashdak Meshukiiba] Sa ', 'Ni Pa Sa [Ashdak Meshukiiba]')
        ]

        for raw_type, line, expected_line in cases:
            with self.subTest(raw_type):
                code = TradeCodes(line)
                result, msg = code.is_well_formed()
                self.assertTrue(result, msg)
                self.assertEqual(1, len(code.sophont_list))
                self.assertEqual(1, len(code.homeworld_list))
                self.assertEqual(['AshdW'], code.sophonts, 'Unexpected sophont list')
                self.assertEqual(['Ashdak Meshukiiba'], code.homeworld_list, 'Unexpected homeworld list')
                self.assertEqual(expected_line, str(code))

    def testSophontDiebackAlongsideActivePopulations(self) -> None:
        line = 'An Asla1 Cs Hi MiyaX S\'mr0'
        code = TradeCodes(line)
        result, msg = code.is_well_formed()
        self.assertTrue(result, msg)
        self.assertEqual(1, len(code.homeworld_list))
        self.assertEqual(["MiyaX"], code.homeworld_list)
        self.assertEqual(["Asla1", "S\'mr0", "MiyaX"], code.sophont_list)

    def testAvoidFakeoutHomeworldAtEnd(self) -> None:
        line = '000000000(0) 00'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldAtStart(self) -> None:
        line = '(0)000000000 00'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldInMiddle(self) -> None:
        line = '00000000000(0)0'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testAvoidFakeoutHomeworldWithSpace(self) -> None:
        line = '000000000000( )'
        code = TradeCodes(line)
        self.assertEqual(0, len(code.sophont_list), "Fake homeworld code should not result in sophont")
        self.assertEqual(0, len(code.homeworld_list), "Fake homeworld code should not result in homeworld")

    def testVerifyActualHomeworld(self) -> None:
        line = '(0000)W'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in sophont")

    def testVerifyHomeworldDoesNotDuplicate(self) -> None:
        line = '(Ashd)W Ni Pa Sa'
        code = TradeCodes(line)
        self.assertEqual(1, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in sophont")

        nuline = str(code)
        self.assertEqual(line, nuline)

    def testVerifyHomeworldWithUnknownPopCountsAsZero(self) -> None:
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

    def testVerifyHomeworldMinorRace(self) -> None:
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

    def testVerifyHomeworldMajorRaceImplicitPop(self) -> None:
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

    def testVerifyHomeworldMajorRaceExplicitPop(self) -> None:
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

    def testVerifyDeadworldDoesntSpawnHomeworld(self) -> None:
        line = '(Miya)X An Asla1 Cs Hi S\'mr0'
        code = TradeCodes(line)
        self.assertEqual(3, len(code.sophont_list), "Actual homeworld code should result in sophont")
        self.assertEqual(1, len(code.homeworld_list), "Actual homeworld code should result in homeworld")

        expected = '(Miya)X An Asla1 Cs Hi S\'mr0'
        self.assertEqual(expected, str(code), "Unexpected trade code result")

    def testVerifyCompactChirperCodeProcessing(self) -> None:
        poplevel = '0123456789W'

        for rawcode in poplevel:
            with self.subTest("Population code " + rawcode):
                line = 'C' + rawcode
                code = TradeCodes(line)
                expected = 'Chir' + rawcode
                self.assertEqual(1, len(code.sophont_list), "Compacted Chirper code should result in sophont")
                self.assertEqual(expected, str(code))

    def testVerifyCompactDroyneCodeProcessing(self) -> None:
        poplevel = '0123456789W'

        for rawcode in poplevel:
            with self.subTest("Population code " + rawcode):
                line = 'D' + rawcode
                code = TradeCodes(line)
                expected = 'Droy' + rawcode
                self.assertEqual(1, len(code.sophont_list), "Compacted Droyne code should result in sophont")
                self.assertEqual(expected, str(code))

    def testSharedHomeworld(self) -> None:
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

    def testHandleOverlyLongSophontName(self) -> None:
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

    def test_is_well_formed(self) -> None:
        cases = [
            ('', '', True, ''),
            ('RsA RsB', 'RsA RsB', False, 'At most one research station allowed'),
            ('Ba Ri St', 'Ba Ri St', False, 'Code pair(s) ("Ba", "Ri"), ("Ba", "St"), ("Ri", "St") not in allowed list'),
            ('DolpW HumaW', '', False, 'Can only have at most one W-pop sophont'),
            ('((Foo)', '(Foo)', True, ''),
            ('Ba X(Solomani)', 'Ba', True, ''),
            ('[Dolp] Ri', 'Ri [Dolp]', True, '')
        ]

        for tradecode, exp_tradecode, is_well_formed, exp_msg in cases:
            with self.subTest(tradecode):
                try:
                    code = TradeCodes(tradecode)
                    self.assertEqual(exp_tradecode, str(code))
                    result, msg = code.is_well_formed()
                    self.assertEqual(is_well_formed, result)
                    self.assertEqual(exp_msg, msg)
                except MultipleWPopError as e:
                    self.assertFalse(is_well_formed)
                    self.assertEqual(exp_msg, str(e))

    def test_is_well_formed_modify(self) -> None:
        cases = [
            (('DolpW', 'HumaW'), ('DolpW', 'HumaW'), 'DolpW HumaW', False, 'Residual code DolpW not in allowed residual list'),
            (('Ba', 'N1'), ('Ba', 'N1'), 'Ba N1', False, 'Code pair(s) ("Ba", "N1") not in allowed list'),
            (('Ri', 'Ri'), (), 'Ri Ri', False, 'At least one trade code duplicated'),
            (('RsA', 'RsB'), (), 'RsA RsB', False, 'At most one research station allowed'),
            (('Ba', 'Xo'), ('Ba', 'Xo'), 'Ba Xo', False, 'Residual code Xo not in allowed residual list'),
            (('Mr', 'Ba'), ('Mr', 'Ba'), 'Ba Mr', True, ''),
            (('[Dolp]', 'Ri'), ('[Dolp]', 'Ri'), 'Ri [Dolp]', True, '')
        ]

        for tradecode, residual, exp_tradecode, is_well_formed, exp_msg in cases:
            with self.subTest(str(tradecode)):
                code = TradeCodes('')
                code.codeset = residual
                code.codes = tradecode
                self.assertEqual(exp_tradecode, str(code))
                result, msg = code.is_well_formed()
                self.assertEqual(is_well_formed, result)
                self.assertIsNotNone(msg)
                self.assertEqual(exp_msg, msg)

    def test_is_well_formed_sophont(self) -> None:
        cases = [
            (['DolpW', 'HumaW'], '', False, 'Can only have at most one W-pop sophont.  Have DolpW HumaW'),
            (['HumanW'], '', False, 'Sophont codes must be no more than 5 chars each - got at least HumanW')
        ]

        for tradecode, exp_tradecode, is_well_formed, exp_msg in cases:
            with self.subTest(str(tradecode)):
                code = TradeCodes('')
                code.sophont_list = tradecode
                self.assertEqual(exp_tradecode, str(code))
                result, msg = code.is_well_formed()
                self.assertEqual(is_well_formed, result)
                self.assertEqual(exp_msg, msg)

    def test_planet_codes(self) -> None:
        code = TradeCodes('In Hi')
        expected = 'Hi In'
        self.assertEqual(expected, code.planet_codes())

    def test_owned_by(self) -> None:
        cases = [
            ('6', {}, None),
            ('6', {'Mr'}, 'Mr'),
            ('7', {'Mr'}, 'Mr'),
            ('7', {}, 'None (Core 0202)'),
            ('8', {'O:'}, 'XXXX'),
            ('8', {'O:Dagu-3240'}, 'Dagu-3240'),
            ('5', {'Re'}, 'Re'),
            ('5', {'Px'}, 'Px')
        ]
        sector = Sector('# Core', '# 0, 0')

        for star_gov, dcode, exp_owned_by in cases:
            with self.subTest(str(star_gov) + " " + str(dcode)):
                star = Star()
                star.position = '0202'
                star.sector = sector
                star.uwp = UWP('?????' + star_gov + '?-?')
                code = TradeCodes('')
                code.dcode = list(dcode)
                self.assertEqual(str(exp_owned_by), str(code.owned_by(star)))

    def test_owners(self) -> None:
        cases = [
            ('O:1010', None, ['O:1010']),
            ('O:1010', 'Fnordia', ['O:Fnor-1010']),
            ('O:Dagu-1010', 'Fnordia', ['O:Dagu-1010']),
            ('O:-1010', 'Fnordia', ['O:-1010']),
        ]

        for owned_code, sector_name, exp_owners in cases:
            with self.subTest(owned_code):
                code = TradeCodes('')
                code.owned.append(owned_code)
                self.assertEqual(exp_owners, code.owners(sector_name))

    def test_colonies(self) -> None:
        cases = [
            ('C:1010', None, ['C:1010']),
            ('C:1010', 'Fnordia', ['C:Fnor-1010']),
            ('C:Dagu-1010', 'Fnordia', ['C:Dagu-1010']),
            ('C:-1010', 'Fnordia', ['C:-1010']),
        ]

        for owned_code, sector_name, exp_owners in cases:
            with self.subTest(owned_code):
                code = TradeCodes('')
                code.owned.append(owned_code)
                self.assertEqual(exp_owners, code.colonies(sector_name))

    def test_canonicalise(self) -> None:
        cases = [
            ('X000000-C', '', 'As Ba Va'),
            ('X0X0000-C', '', 'Ba'),
            ('X00X000-C', '', 'Ba'),
            ('X01A300-5', '', 'Ic Lo'),
            ('X020600-5', '', 'De Na Ni Po'),
            ('X2AA800-5', '', 'Fl Ph'),
            ('XAA3900-5', '', 'Fl Hi In'),
            ('X9DA300-5', '', 'Lo Wa'),
            ('X9AA300-5', '', 'Fl Lo'),
            ('X9A0000-5', '', 'Ba He'),
            ('XAA0000-5', '', 'Ba He'),
            ('X9XA300-5', '', 'Lo'),
            ('X9DX300-5', '', 'Lo'),
            ('X655700-5', '', 'Ag Ga'),
            ('X6X7700-5', '', ''),
            ('X65X700-5', '', ''),
            ('XADA300-5', '', 'Lo Oc'),
            ('XADX300-5', '', 'Lo'),
            ('XAAA300-5', '', 'Fl Lo'),
            ('XAAX300-5', '', 'Lo'),
            ('XAD9300-5', '', 'Lo'),
            ('XAA4400-5', '', 'Fl Ni'),
            ('X888800-8', '', 'Pa Ph Ri'),
            ('XAAX800-6', '', 'Ph'),
            ('XAX2800-6', '', 'Ph'),
            ('X123600-9', '', 'Na Ni Po'),
            ('X12X600-9', '', 'Ni'),
            ('X034600-3', '', 'Ni'),
            ('X443400-3', '', 'Ni Po'),
            ('X4X4400-3', '', 'Ni'),
            ('X4X6500-6', '', 'Ni'),
            ('XAXA000-0', '', 'Ba'),
            ('X54X400-0', '', 'Ni'),
            ('X6X7900-A', '', 'Hi'),
            ('X555555-5', 'O:0202 C:0202', 'Ag Ni'),
            ('X777777-7', 'Ba Lo Ni Ph Hi', 'Ag Pi')
        ]
        sector = Sector('# Core', '# 0, 0')

        for uwp, init_code, exp_code in cases:
            with self.subTest(uwp + " " + init_code):
                star = Star()
                star.position = '0202'
                star.sector = sector
                star.uwp = UWP(uwp)
                star.tradeCode = TradeCodes(init_code)
                star.tradeCode.canonicalise(star)
                self.assertEqual(exp_code, str(star.tradeCode))

    def test_canonicalise_out_of_bounds(self) -> None:
        cases = [
            ('X33A000-4', '', '1', 'Ba'),
            ('X655000-4', '', '1', 'Ba'),
            ('X000000-0', '', '1', 'Ba'),
            ('XADA000-0', '', '1', 'Ba'),
            ('X500700-0', '', '4', 'Va'),
            ('X544100-0', '', '4', ''),
            ('X644500-0', '', '4', ''),
            ('X564500-4', '', '4', ''),
            ('X566600-8', '', '4', ''),
            ('X320000-0', '', '1', 'Ba')
        ]
        sector = Sector('# Core', '# 0, 0')
        mods = ['port', 'size', 'atmo', 'hydro', 'pop', 'gov', 'law']

        for uwp, init_code, set_x, exp_code in cases:
            with self.subTest(uwp + " " + init_code):
                star = Star()
                star.position = '0202'
                star.sector = sector
                star.uwp = UWP(uwp)
                for raw_item in set_x:
                    item = int(raw_item)
                    star.uwp.__setattr__(mods[item], 'X')

                star.tradeCode = TradeCodes(init_code)
                star.tradeCode.canonicalise(star)
                self.assertEqual(exp_code, str(star.tradeCode))

    def test_check_canonical_no_msg(self) -> None:
        cases = [
            ('X01A300-5', 'Ic Lo Ni', 'Ic Lo Ni', False,
             ['None (Core None)-X01A300-5 Found invalid "Ni" code on world with 3 population: [\'Ic\', \'Lo\', \'Ni\']'],
             False),
            ('X01A300-5', 'Ic', 'Ic', False,
             ['None (Core None)-X01A300-5 Calculated "Lo" not in trade codes [\'Ic\']'],
             False),
            ('X01A300-5', 'Lo', 'Lo', False,
             ['None (Core None)-X01A300-5 Calculated "Ic" not in trade codes [\'Lo\']'],
             False),
            ('X01A300-5', 'He Ic Lo', 'He Ic Lo', False,
             ['None (Core None)-X01A300-5 Found invalid "He" in trade codes: [\'He\', \'Ic\', \'Lo\']'],
             False),
            ('X01A300-5', 'Ri Ic Lo', 'Ic Lo Ri', False,
             ['None (Core None)-X01A300-5 Found invalid "Ri" in trade codes: [\'Ic\', \'Lo\', \'Ri\']'],
             False),
            ('C066766-9', 'Ag', 'Ag', False,
             ['None (Core None)-C066766-9 Calculated "Ri" not in trade codes [\'Ag\']'],
             False
             ),
            ('C666766-9', 'Ag Ri De', 'Ag De Ri', False,
             [
                 'None (Core None)-C666766-9 Found invalid "De" in trade codes: [\'Ag\', \'De\', \'Ri\']',
                 'None (Core None)-C666766-9 Calculated "Ga" not in trade codes [\'Ag\', \'De\', \'Ri\']'
             ],
             False
             ),
            ('X00A300-5', 'Va Lo Ni', 'Lo Ni Va', False,
             [
                 'None (Core None)-X00A300-5 Calculated "Ic" not in trade codes [\'Lo\', \'Ni\', \'Va\']',
                 'None (Core None)-X00A300-5 Found invalid "Ni" code on world with 3 population: [\'Lo\', \'Ni\', \'Va\']'
             ],
             False),
            ('X00A900-5', 'In', 'Hi In', False,
             [
                 'None (Core None)-X00A900-5 Calculated "Ic" not in trade codes [\'In\', \'Hi\']',
                 'None (Core None)-X00A900-5 Calculated "Va" not in trade codes [\'In\', \'Hi\']'
             ],
             False),
            ('X000700-5', 'As', 'As Va', False,
             [
                 'None (Core None)-X000700-5 Calculated "Na" not in trade codes [\'As\', \'Va\']',
                 'None (Core None)-X000700-5 Calculated "Pi" not in trade codes [\'As\', \'Va\']'
             ],
             False),
            ('X000700-5', 'As Ba Lo Ni', 'As Va', True,
             [
                 'None (Core None)-X000700-5 Calculated "Na" not in trade codes [\'As\', \'Va\']',
                 'None (Core None)-X000700-5 Calculated "Pi" not in trade codes [\'As\', \'Va\']'
             ],
             False),
        ]
        sector = Sector('# Core', '# 0, 0')
        for uwp, trade_code, exp_trade, fix_pop, exp_msg, expected in cases:
            with self.subTest(uwp + " " + trade_code):
                star = Star()
                star.sector = sector
                star.uwp = UWP(uwp)
                star.tradeCode = TradeCodes(trade_code)

                msg = []
                with self.assertLogs(self.logger, level='ERROR') as log:
                    star.tradeCode.check_world_codes(star, msg, fix_pop=fix_pop)
                    output = log.output
                    self.assertEqual(len(exp_msg), len(output), output)
                    for line in exp_msg:
                        output = [item for item in output if line not in item]
                    self.assertEqual(0, len(output), output)
                self.assertEqual(exp_msg, msg)
                self.assertEqual(expected, star.tradeCode.check_world_codes(star, fix_pop=fix_pop))
                self.assertEqual(exp_trade, str(star.tradeCode))

    def test_check_canonical_no_msg_out_of_bounds(self) -> None:
        cases = [
            ('X01A300-5', 'De Lo Ni',
             '1',
             [
                 'None (Core None)-XX1A300-5 Found invalid "De" in trade codes: [\'De\', \'Lo\', \'Ni\']',
                 'None (Core None)-XX1A300-5 Found invalid "Ni" code on world with 3 population: [\'De\', \'Lo\', \'Ni\']'
             ],
             False),
            ('X01A300-5', 'De Lo Ni',
             '2',
             [
                 'None (Core None)-X0XA300-5 Found invalid "De" in trade codes: [\'De\', \'Lo\', \'Ni\']',
                 'None (Core None)-X0XA300-5 Found invalid "Ni" code on world with 3 population: [\'De\', \'Lo\', \'Ni\']'
             ],
             False),
            ('X01A300-5', 'De Lo Ni',
             '3',
             [
                 'None (Core None)-X01X300-5 Found invalid "De" in trade codes: [\'De\', \'Lo\', \'Ni\']',
                 'None (Core None)-X01X300-5 Found invalid "Ni" code on world with 3 population: [\'De\', \'Lo\', \'Ni\']'
             ],
             False),
            ('X00A300-5', 'Va Lo Ni',
             '3',
             [
                 'None (Core None)-X00X300-5 Found invalid "Va" in trade codes: [\'Lo\', \'Ni\', \'Va\']',
                 'None (Core None)-X00X300-5 Found invalid "Ni" code on world with 3 population: [\'Lo\', \'Ni\', \'Va\']'
             ],
             False),
            ('X06A500-5', 'Pr',
             '3',
             [
                 'None (Core None)-X06X500-5 Found invalid "Pr" in trade codes: [\'Pr\']',
                 'None (Core None)-X06X500-5 Calculated "Ni" not in trade codes [\'Pr\']'
             ],
             False),
            ('X00AA00-8', 'In',
             '2',
             [
                 'None (Core None)-X0XAA00-8 Found invalid "In" in trade codes: [\'In\']',
                 'None (Core None)-X0XAA00-8 Calculated "Hi" not in trade codes [\'In\']'
             ],
             False
            ),
            ('X00AA00-8', 'In',
             '4',
             [
                 'None (Core None)-X00AX00-8 Found invalid "In" in trade codes: [\'In\']',
                 'None (Core None)-X00AX00-8 Calculated "Ic" not in trade codes [\'In\']',
                 'None (Core None)-X00AX00-8 Calculated "Va" not in trade codes [\'In\']'
             ],
             False
             ),
            ('X000A00-8', '',
             '1',
             [
                 'None (Core None)-XX00A00-8 Calculated "In" not in trade codes []',
                 'None (Core None)-XX00A00-8 Calculated "Na" not in trade codes []',
                 'None (Core None)-XX00A00-8 Calculated "Hi" not in trade codes []'
             ],
             False
             ),
            ('X000A00-8', '',
             '2',
             [
                 'None (Core None)-X0X0A00-8 Calculated "Hi" not in trade codes []'
             ],
             False
             ),
        ]
        sector = Sector('# Core', '# 0, 0')
        mods = ['port', 'size', 'atmo', 'hydro', 'pop', 'gov', 'law']
        for uwp, trade_code, set_x, exp_msg, expected in cases:
            with self.subTest(uwp + " " + set_x + " " + trade_code):
                star = Star()
                star.sector = sector
                star.uwp = UWP(uwp)
                for raw_item in set_x:
                    item = int(raw_item)
                    star.uwp.__setattr__(mods[item], 'X')
                star.tradeCode = TradeCodes(trade_code)

                msg = []
                with self.assertLogs(self.logger, level='ERROR') as log:
                    star.tradeCode.logger.error('Dummy error message')
                    star.tradeCode.check_world_codes(star, msg)
                    output = log.output
                    self.assertEqual(len(exp_msg) + 1, len(output), output)
                    for line in exp_msg:
                        output = [item for item in output if line not in item]
                    self.assertEqual(1, len(output), output)
                self.assertEqual(exp_msg, msg)
                self.assertEqual(expected, star.tradeCode.check_world_codes(star))

    def test_check_canonical_synthetic_planet_code_out_of_bounds(self) -> None:
        cases = [
            ('X6A6300-5', 'Va',
             '2',
             [
                 'None (Core None)-X6X6300-5 Found invalid "Va" in trade codes: [\'Va\']',
             ],
             False),
            ('X6A6300-5', 'Va',
             '',
             [],
             True),
        ]
        sector = Sector('# Core', '# 0, 0')
        mods = ['port', 'size', 'atmo', 'hydro', 'pop', 'gov', 'law']
        for uwp, trade_code, set_x, exp_msg, expected in cases:
            star = Star()
            star.sector = sector
            star.uwp = UWP(uwp)
            for raw_item in set_x:
                item = int(raw_item)
                star.uwp.__setattr__(mods[item], 'X')
            star.tradeCode = TradeCodes(trade_code)

            with self.assertLogs(self.logger, level='ERROR') as log:
                star.tradeCode.logger.error('Dummy error message')
                actual = star.tradeCode._check_planet_code(star, 'Va', '678', None, '678')
                self.assertEqual(expected, actual)
                output = log.output
                self.assertEqual(len(exp_msg) + 1, len(output), output)
                for line in exp_msg:
                    output = [item for item in output if line not in item]
                self.assertEqual(1, len(output), output)

    def test_check_canonical_synthetic_economic_code_out_of_bounds(self) -> None:
        cases = [
            ('X6A6600-5', 'Pr',
             '2',
             [
                 'None (Core None)-X6X6600-5 Found invalid "Pr" in trade codes: [\'Pr\']',
             ],
             False),
            ('X6A6600-5', 'Pr',
             '4',
             [
                 'None (Core None)-X6A6X00-5 Found invalid "Pr" in trade codes: [\'Pr\']',
             ],
             False),
            ('X6A6600-5', 'Pr',
             '',
             [],
             True),
        ]
        sector = Sector('# Core', '# 0, 0')
        mods = ['port', 'size', 'atmo', 'hydro', 'pop', 'gov', 'law']
        for uwp, trade_code, set_x, exp_msg, expected in cases:
            with self.subTest(uwp + " " + set_x + " " + trade_code):
                star = Star()
                star.sector = sector
                star.uwp = UWP(uwp)
                for raw_item in set_x:
                    item = int(raw_item)
                    star.uwp.__setattr__(mods[item], 'X')
                star.tradeCode = TradeCodes(trade_code)

                with self.assertLogs(self.logger, level='ERROR') as log:
                    star.tradeCode.logger.error('Dummy error message')
                    actual = star.tradeCode._check_econ_code(star, 'Pr', None, '678', None)
                    self.assertEqual(expected, actual)
                    output = log.output
                    self.assertEqual(len(exp_msg) + 1, len(output), output)
                    for line in exp_msg:
                        output = [item for item in output if line not in item]
                    self.assertEqual(1, len(output), output)

    def test_fix_synthetic_economic_code_out_of_bounds(self) -> None:
        cases = [
            ('X578800-9', 'Pi', '2', ''),
            ('X578800-9', 'Pi', '4', ''),
            ('X5A8A00-9', 'Pi', '', 'Pi')
        ]
        sector = Sector('# Core', '# 0, 0')
        mods = ['port', 'size', 'atmo', 'hydro', 'pop', 'gov', 'law']
        for uwp, trade_code, set_x, exp_trade in cases:
            with self.subTest(uwp):
                star = Star()
                star.sector = sector
                star.uwp = UWP(uwp)
                for raw_item in set_x:
                    item = int(raw_item)
                    star.uwp.__setattr__(mods[item], 'X')
                star.tradeCode = TradeCodes(trade_code)
                star.tradeCode._fix_econ_code(star, 'Pi', None, '678', None)
                self.assertEqual(exp_trade, str(star.tradeCode))

    def test_trim_ill_formed_residual_codes(self) -> None:
        cases = [
            ('(Foobar', False),
            ('{Foobar', False),
            ('[Foobar', False),
            ('Foobar)', False),
            ('Foobar)', False),
            ('Foobar)', False),
            ('{Fuel}', True),
            ('XX{XXFuel}', False),
            ('Cp', True),
            ('[Bar]', True),
            ('[Bar]W', True),
            ('(Foo)', True),
            ('(Foo)?', True),
            ('(Foo)8', True),
            ('(Foo)81', False),
            ('Di(Foo)', True),
            ('0000000000000', False),
            ('[0000000000000', False),
            ('[000000000000]', False),
            ('[00000000000]', False),
            ('[0000000000]', True),
            ('Lt', True),
            ('As', True),
        ]

        for trade_code, temp in cases:
            with self.subTest(trade_code):
                tradeCode = TradeCodes('')
                tradeCode.codes.append(trade_code)
                tradeCode.codeset.append(trade_code)
                tradeCode.logger.manager.disable = 0

                with self.assertLogs(tradeCode.logger, level='WARNING') as log:
                    tradeCode.logger.warning('Dummy error message')
                    tradeCode.trim_ill_formed_residual_codes()
                    if temp:
                        self.assertEqual(trade_code, str(trade_code))
                    else:
                        self.assertEqual('', str(tradeCode))

                    exp_msg = ["Residual code " + str(trade_code) + " not in allowed residual list - removing"]
                    output = log.output
                    self.assertEqual(1 + (1 if not temp else 0), len(output), output)
                    for line in exp_msg:
                        output = [item for item in output if line not in item]
                    self.assertEqual(1, len(output), output)

    def test_preprocess_initial_trade_codes(self) -> None:
        cases = [
            ('Ba Ba As', 'As Ba', []),
            ('Ba    As', 'As Ba', []),
            (')', '', []),
            ('[ Ga A(Foob)', 'Ga', []),
            ('A(Fooba)', '', []),
            ('A()Foob Ba', 'Ba', []),
            ('( Ga', 'Ga', []),
            ('XXXX', '', ['XXXX']),
            ('XX)XX', 'XX)XX', []),
            ('X(XX)XX', '', []),
            ('X(XX)XX]XX', '', []),
            (') Ba', 'Ba', []),
            (')] Ba', 'Ba', []),
            ('])Ba', '', []),
            ('XX)]XX Ba', 'Ba', ['XX)]XX']),
            ('XX])XX Ba', 'Ba', ['XX])XX']),
            ('[[Foob]', '[Foob]', []),
            ('XX[[XX', '', ['XX[[XX']),
            ('Di(Foob) Ga', 'Di(Foob) Ga', []),
            ('Di(Foo Bar)0 Ga', 'Di(Foo Bar) Ga', []),
            ('Di(Foo B)0 Ga', 'Di(Foo B) Ga', []),
            ('Di(Foo )0 Ga', 'Ga', [')0']),
            ('Di(Foob)', 'Di(Foob)', []),
            ('Di(Foo bar)', 'Di(Foo bar)', []),
            ('GDi(Di(Foo bar)', 'Di(Di(Foo bar)', ['G']),
            ('[]Ba ()Ga', 'Ba Ga', []),
            ('VaDi(Foob)', 'Di(Foob) Va', []),
            ('XXDi(XXFoob)', 'Di(XXFoob)', ['XX']),
            ('(Foobarbaz)Q', '(Foobarbaz)', []),
            ('(Fooba)W', '(Fooba)W', []),
            ('(Fooba)', '(Fooba)', []),
            ('(Fooba r)', '(Fooba r)', []),
            ('(Foob)67', '(Foob)6', []),
            ('[Fooba]W', '[Fooba]W', []),
            ('[Foo Bar]W Ga', 'Ga [Foo Bar]W', []),
            ('(Foo Bar)W', '(Foo Bar)W', []),
            ('(Foo Bar)Q Ga', '(Foo Bar) Ga', []),
            ('(Foo Bar)Qa Ga', 'Ga', ['Bar)Qa']),
            ('[Fooba)', '', ['[Fooba)']),
            ('(Fooba]', '', ['(Fooba]']),
            ('[0000000)(]X', '[0000000)(]X', []),
            ('[000)(]X (00)Q (0000)Q', '(0000)Q [000)(]X', []),
            ('[000)(]X (00)Q (0)00)Q', '[000)(]X', ['(0)00)Q']),
            ('[00)(]X', '[00)(]X', []),
            ('XX]XX', 'XX]XX', []),
            ('[00000000000000 - Ga', 'Ga', ['-']),
            ('[0000000)(]X [', '[0000000)(]X', []),
            ('C0 D0 Ga', 'Chir0 Droy0 Ga', []),
            ('[[[Fooba]]]', '[Fooba]', []),
            ('(((Fooba)))', '(Fooba)', []),
            ('(FoobaFoobaFoobaFoobaFoobaFoobaFoob)', '(FoobaFoobaFoobaFoobaFoobaFoobaFoob)', []),
            ('(FoobaFoobaFoobaFoobaFoobaFoobaFooba)', '(FoobaFoobaFoobaFoobaFoobaFoobaFooba)', []),
            ('(FoobaFoobaFoobaFoobaFoobaFoobaFoobaF)', '(FoobaFoobaFoobaFoobaFoobaFoobaFooba)', []),
        ]

        for init_trade, exp_code, exp_residuals in cases:
            with self.subTest(init_trade):
                logger = logging.getLogger('PyRoute.TradeCodes')
                logger.manager.disable = 0

                with self.assertLogs(logger, 'WARNING') as logs:
                    logger.warning('Dummy Message')
                    code = TradeCodes(init_trade)
                    self.assertEqual(exp_code, str(code))

                    output = logs.output
                    self.assertEqual(1 + len(exp_residuals), len(output))
                    for resid in exp_residuals:
                        output = [item for item in output if ' ' + resid + ' ' not in item]
                    self.assertEqual(1, len(output))

    def test_process_sophonts_and_homeworlds(self) -> None:
        cases = [
            ('[[Foobar]', ['FoobW'], ['Foobar']),
            ('(Foobar)', ['FoobW'], ['Foobar']),
            ('(Foobar)W', ['FoobW'], ['Foobar']),
            ('[Foobar]W', ['FoobW'], ['Foobar']),
            ('Di(Foobar)', ['FoobX'], ['DiFoobar']),
            ('(Foo)5 [Foo]5', ['FooX5', 'FooX5'], ['Foo', 'Foo']),
            ('(Foo]b)', [], []),
            ('(Ba[r)', [], []),
            ('(XXXX)', ['XXXXW'], ['XXXX']),
            ('(A)', ['AXXXW'], ['A']),
            ('Fooba5', [], []),
            ('(K\'kr)5', ['KXkr5'], ["K'kr"]),
            ('(G!na)5', ['GXna5'], ['G!na']),
            ('(G!na)X', ['GXnaX'], ['G!na']),
            ('(G!na)?', ['GXna0'], ['G!na']),
            ('(Foo Bar)', ['FooXW'], ['Foo Bar']),
            ('[][][]', [], []),
            ('[][][Foo Bar]', ['FooXW'], ['Foo Bar']),
        ]

        for init_trade, sophont_list, homeworld_list in cases:
            with self.subTest(init_trade):
                code = TradeCodes(init_trade)
                self.assertEqual(sophont_list, code.sophont_list)
                self.assertEqual(homeworld_list, code.homeworld_list)

    def test_process_sophonts_and_homeworld_multiple_w_pop(self) -> None:
        cases = [
            ('[Foo] (Bar)'),
            ('[Foo]W (Bar)W'),
            ('[Foo]  DolpW')
        ]
        expected = "Can only have at most one W-pop sophont"
        for init_trade in cases:
            with self.subTest(init_trade):
                msg = None
                try:
                    TradeCodes(init_trade)
                except MultipleWPopError as e:
                    msg = str(e)
                self.assertEqual(expected, msg)

    def test_process_homeworld(self) -> None:
        cases = [
             ('[Barfoo]', [], '[Barfoo]', ['BarfW', 'BarfW'], ['Barfoo', '[Barfoo]']),
             ('(Barfoo)', [], '(Barfoo)', ['BarfW', 'BarfW'], ['Barfoo', 'Barfoo']),
             ('', [], 'barfoo', [], []),
        ]

        for homeworld, homeworld_list, init_trade, exp_sophont, exp_homeworld in cases:
            with self.subTest(init_trade):
                code = TradeCodes(init_trade)
                logger = code.logger
                with self.assertLogs(logger, "WARNING") as logs:
                    try:
                        code._process_homeworld(homeworld, homeworld_list, init_trade)
                    except SystemExit as e:
                        output = logs.output
                        self.assertEqual(1, len(output))
                        expected = "Unable to process barfoo"
                        self.assertIn(expected, output[0])
                        self.assertTrue(output[0].endswith(expected))
                        self.assertEqual('1', str(e))
                        return
                    logger.warning("Dummy message")
                    self.assertEqual([homeworld], homeworld_list)
                    self.assertEqual(exp_sophont, code.sophont_list)
                    self.assertEqual(exp_homeworld, code.homeworld_list)

    def test_process_deadworld(self) -> None:
        cases = [
            ('DiFoobar', ['DiFoobar'], ['DiFoX'], ['DiFoobar'], 'Di(Foobar)'),
            ('Di(Foobar)', ['DiFoobar'], ['DiFoX'], ['DiFoobar'], 'Di(Foobar)'),
            ('(Foobar)X', [], ['FoobX'], ['FoobarX'], '(Foobar)X')
        ]
        for homeworld, working_list, soph_list, home_list, init_trade in cases:
            with self.subTest(init_trade):
                code = TradeCodes('')
                old_len = len(working_list)
                old_list = copy.deepcopy(working_list)
                code._process_deadworld(homeworld, working_list)
                self.assertEqual(old_len + 1, len(working_list))
                old_list.append(homeworld)
                self.assertEqual(old_list, working_list)
                self.assertEqual(soph_list, code.sophont_list)
                self.assertEqual(home_list, code.homeworld_list)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

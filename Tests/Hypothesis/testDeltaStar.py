import contextlib
import copy
from datetime import timedelta
import logging
import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, lists, from_regex, composite, sampled_from, integers, floats

from PyRoute.AreaItems.Sector import Sector
from PyRoute.DeltaStar import DeltaStar
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.TradeCodes import TradeCodes

tradecodes = []


@composite
def trade_code(draw):
    if 0 == len(tradecodes):
        tradecodes.extend(TradeCodes.pcodes)
        tradecodes.extend(TradeCodes.dcodes)
        tradecodes.extend(TradeCodes.ext_codes)
        tradecodes.extend(TradeCodes.allowed_residual_codes)

    strat = sampled_from(tradecodes)

    return draw(lists(strat, min_size=2, max_size=12))


@composite
def starline(draw, barren_world=False):
    col = draw(integers(min_value=1, max_value=32))
    row = draw(integers(min_value=1, max_value=40))
    posn = str(col).rjust(2, '0') + str(row).rjust(2, '0')

    name = draw(text(min_size=1, max_size=15)).ljust(20)

    port = draw(text(min_size=1, max_size=1, alphabet="ABCDEX"))
    uwp_alphabet = '0123456789ABCDEFGH'

    uwp = port + draw(text(min_size=6, max_size=6, alphabet=uwp_alphabet)) + '-' + draw(text(min_size=1, max_size=1, alphabet=uwp_alphabet))
    if barren_world:
        uwp = uwp[0:4] + "0" + uwp[5:]

    # TODO - tradecode picks
    trade_array = draw(trade_code())
    if barren_world:
        trade_array.append('Ba')
    tradeCodes = ' '.join(trade_array)

    extension_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # importance gets autogenned
    importance = '{ 0 }'

    # ex
    ex_tail = draw(integers(min_value=-5, max_value=5))
    stub = str(ex_tail) if 0 > ex_tail else '+' + str(ex_tail)

    ex = '(' + draw(text(min_size=3, max_size=3, alphabet=extension_alphabet)) + stub + ')'

    # cx
    cx = '[' + draw(text(min_size=4, max_size=4, alphabet=extension_alphabet)) + ']'

    flip = draw(floats(min_value=0.0, max_value=1.0))

    noble_alphabet = 'BcCDeEfFGH'
    nobles = '-' if 0.7 < flip else draw(text(min_size=1, max_size=5, alphabet=noble_alphabet))

    base = '-'
    tradezone = draw(text(min_size=1, max_size=1, alphabet='-ARUF--'))

    pbg = draw(text(min_size=3, max_size=3, alphabet='0123456789'))

    worlds = str(draw(integers(min_value=0, max_value=12)))

    alg = 'NaHu'

    star = 'G5 V'

    starline = posn + ' ' + name + ' ' + uwp + ' ' + tradeCodes.ljust(38) + ' ' + importance + ' ' + ex + ' ' + cx + ' ' \
               + nobles + ' ' + base + ' ' + tradezone + ' ' + pbg + ' ' + worlds + ' ' + alg + ' ' + star

    return starline


@composite
def mixed_starline(draw):
    choice = draw(floats(min_value=0.0, max_value=1.0))
    if 0.5 < choice:
        res = from_regex(regex=ParseStarInput.starline,
                      alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*')
    else:
        res = starline()
    return draw(res)


class testDeltaStar(unittest.TestCase):

    def test_plain_canonicalisation(self):
        cases = [
            # Commented out for the moment - Barren/Dieback is a bit more intricate than other pop codes, and don't want
            # perfect to be the enemy of good
            # ('0917 Deyis II             E874000-0 Ba Da (Kebkh) Re                      { -3 } (200-5) [0000] -     -  A 000 10 ImDi K4 II                                                        ',
            #  '0917 Deyis II             E874000-2 Ba Da Di(Kebkh) Re                    { -3 } (200-5) [0000] -    -  A 000 10 ImDi K4 II                                                   '),
            ('0235 Oduart               C7B3004-5 Fl Di(Oduart) Da             { -2 } (800+2) [0000] - M  A 004 10 HvFd G4 V M3 V M7 V',
             '0235 Oduart               C7B3004-5 Ba Da Di(Oduart) Fl                   { -2 } (800+0) [0000] -    M  A 004 10 HvFd G4 V M3 V M7 V                                          '),
            ('0101                      X73A000-0 Ba Lo Ni Wa                         - -  - 012   --',
             '0101                      X738000-3 Ba                                    { -3 } -       -      -    -  - 012 0  --                                                           '),
            ('0527 Wellington Base      AEFA422-E Ht Ni Oc                            - M  R 711   He',
             '0527 Wellington Base      AEFA422-B Ht Ni Oc                              { 1 }  -       -      -    M  R 711 0  He                                                           '),
            ('0239 Etromen              CFB8558-B Fl Ni                               - -  A 523   Na',
             '0239 Etromen              CFB8558-8 Fl Ni                                 { -2 } -       -      -    -  A 523 0  Na                                                           '),
            ('1220 Gateway              A002688-B As Ic Na Ni Va Cx      { 1 }  (C55+1) [675B] - -  - 822 16 GaFd A2 V F0 V',
             '1220 Gateway              A000688-A As Cx Na Ni Va                        { 1 }  (C55+1) [675B] -    -  - 822 16 GaFd A2 V F0 V                                               '),
            ('0825 Corstation           C005100-8 As Ic Lo Va            { -2 } (500-5) [1113] - -  - 211 14 GaFd M0 V M1 V',
             '0825 Corstation           C000100-8 As Lo Va                              { -2 } (500-5) [1113] -    -  - 211 14 GaFd M0 V M1 VI                                              '),
            ('3222 Ardh                           C001554-A As Ic Ni Va          {+0} (843+1) [658A] - C - 601   Ve F9 V',
             '3222 Ardh                 C000554-A As Ni Va                              { 0 }  (843+1) [658A] -    C  - 601 0  Ve   F9 V                                                    '),
            ('2738 Taen                           B001685-8 As Ic Ni Na Va       {-1} (J52-2) [3559] - N - 533   Ve M9 V',
             '2738 Taen                 B000685-8 As Na Ni Va                           { -1 } (J52-2) [3559] -    N  - 533 0  Ve   M9 V                                                    '),
            # Population zero, TL 0, alongside a specific dieback should keep the barren
            ('0924 Ognar                X867000-0 Ba Ga Di(Ogna)       {-3 } (300+1) [0000] - -  R 004 10 Og K1 V',
             '0924 Ognar                X867000-2 Ba Di(Ogna) Ga                        { -3 } (300+0) [0000] -    -  R 004 10 Og   K1 V                                                    '),
            # Dieback of two-word sophont name tripped things up
            ('2117 Sabmiqys             A560056-H De Fo Di(Gya Ks)          { 2 }  (600-4) [0000] -    -  R 004 9  ImDa G3 V          ',
             '2117 Sabmiqys             A561056-8 Ba Di(Gya Ks) Fo                      { -1 } (600-0) [0000] -    -  R 004 9  ImDa G3 V                                                    '),
            # Treat Gov code X with population as Gov 0
            ('1702 Eslalyat             B493AXB-A Hi In                               - M  R 211   Dr        ',
             '1702 Eslalyat             B494A5A-B Hi In                                 { 4 }  -       -      -    M  R 211 0  Dr                                                           '),
            # <TL8 worlds should have max resources 12
            ('1620 Daydyor Yashas       X683973-4 Hi Pr                { 1 }  (E8D+2) [9AAD] - -  - 323 14 NaXX F7 V',
             '1620 Daydyor Yashas       X683973-4 Hi Pr                                 { -1 } (C8B+2) [98A9] -    -  - 323 14 NaXX F7 V                                                    '),
            # Atmo should be capped to F, hydro capped to A
            ('1920 Rainbow Sun          AAVV997-D Hi In Sp                            - KM - 223   Na',
             '1920 Rainbow Sun          AAFA997-C Hi Oc Sp                              { 4 }  -       -      -    KM - 223 0  Na                                                           '),
            # TL8+ worlds should have max resources 12 + belts + GGs
            ('1620 Daydyor Yashas       X683973-D Hi Pr                { 1 }  (F8D+2) [9AAD] - -  - 311 14 NaXX F7 V',
             '1620 Daydyor Yashas       X683973-4 Hi Pr                                 { -1 } (C8B+2) [98A9] -    -  - 311 14 NaXX F7 V                                                    '),
        ]

        sector = Sector('# Core', '# 0, 0')
        for line, expected in cases:
            with self.subTest():
                foo = DeltaStar.parse_line_into_star(line, sector, 'fixed', 'fixed')
                self.assertIsNotNone(foo, "Line should parse to star")
                foo.canonicalise()
                foo_string = foo.parse_to_line()

                self.assertEqual(expected, foo_string, 'Unexpected canonicalisation result')

    """
    Given a Star object read in from a starline, trapping log error messages, ensure DeltaStar.check_canonical returns
    same number of messages
    """
    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000000-0                                       { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V ')
    @example('0101 0                    A000000-0                                       { 0 } (000+0) [0000] BBBBB - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0001] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 De                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Ga                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0010] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0100] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000200-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A00B000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000400-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Fl                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (00C+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A001000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000600-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000700-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A020000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 He                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Wa                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A060500-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A044400-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Oc                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A010000-0 Va                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Ri                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 \n                    A000000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Ag                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 Lo                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A00B000-0 Va                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000E00-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    AD01000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    AD20000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As In                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_check_canonicalisation(self, starline):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Core', '# 0, 0')

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
                )
                self.assertEqual(1, len(outer_logs.output), "Dummy log message not in outer_logs")
                inner_logger.debug(
                    'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
                )
                self.assertEqual(1, len(inner_logs.output), "Dummy log message not in inner_logs")

                star1 = None
                allowed_errors = [
                    'Input UWP malformed'
                ]

                try:
                    star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                except ValueError as e:
                    rep = str(e)

                    if rep in allowed_errors:
                        pass
                    else:
                        raise e
                assume(star1 is not None)
                star1.index = 0
                star1.allegiance_base = 'NaHu'
                self.assertIsNotNone(star1, "Fatal failure parsing line: " + starline)
                self.assertTrue(isinstance(star1, DeltaStar), "Error parsing line: " + starline)

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                # trim complaints about calculated importance - that's fixed on import
                output = [line for line in output if "Calculated importance" not in line]
                # trim log lines of less than warning severity - "DEBUG" is set to ensure there will be output to grab
                output = [line for line in output if 'DEBUG:' not in line and 'INFO:' not in line]

                _, canonical_messages = star1.check_canonical()
                for msg in canonical_messages:
                    output = [line for line in output if msg not in line]

                num_output = len(output)
                tail = output[0] if 0 < len(output) else ''
                self.assertEqual(
                    0,
                    num_output,
                    "Mismatch between parsing logs and canonical-check: " + starline + '\n' + tail
                )

    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000000-0 As De                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ga                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Fl                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As He                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A001000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ic                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Oc                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Po                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A010000-0 As Va                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Wa                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Na                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ag                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Pa                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Pi                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Pr                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As In                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ri                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Lo                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ph                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ni                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Hi                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    AE0A000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_canonicalise_invalid_trade_codes(self, starline):
        sector = Sector('# Core', '# 0, 0')
        star1 = None
        allowed_errors = [
            'Input UWP malformed'
        ]

        try:
            star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        except ValueError as e:
            rep = str(e)

            if rep in allowed_errors:
                pass
            else:
                raise e
        assume(star1 is not None)

        star1.index = 0
        star1.allegiance_base = 'NaHu'

        _, canonical_messages = star1.check_canonical()

        star1.canonicalise()

        _, nu_messages = star1.check_canonical()
        invalid = [item for item in nu_messages if 'Found invalid' in item and ('trade codes' in item or 'code on world' in item)]

        self.assertTrue(
            len(canonical_messages) >= len(nu_messages),
            'New canonical-check messages should not happen: \n' + starline
        )
        self.assertEqual(0, len(invalid), 'At least one invalid trade code remaining: \n' + starline)

    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 De De                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000400-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A001000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A020000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000600-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000700-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A0A1000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000800-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A044400-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A044500-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A320000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A33A000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A060500-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    AA3A000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A060600-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A655000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A00B000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000E00-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A320000-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000E00-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    AD00000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    AD20000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_canonicalise_missing_trade_codes(self, starline):
        sector = Sector('# Core', '# 0, 0')
        star1 = None
        allowed_errors = [
            'Input UWP malformed'
        ]

        try:
            star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        except ValueError as e:
            rep = str(e)

            if rep in allowed_errors:
                pass
            else:
                raise e
        assume(star1 is not None)
        star1.index = 0
        star1.allegiance_base = 'NaHu'

        _, canonical_messages = star1.check_canonical()

        star1.canonicalise()

        _, nu_messages = star1.check_canonical()
        invalid = [item for item in nu_messages if 'not in trade codes' in item]

        self.assertTrue(
            len(canonical_messages) >= len(nu_messages),
            'New canonical-check messages should not happen: \n' + starline
        )
        badline = '' if 0 == len(invalid) else invalid[0]
        self.assertEqual(0, len(invalid), 'At least one missing trade code not added: \n' + starline + '\n' + badline)

    @given(starline(barren_world=True))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (000+0) [0001] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (000+0) [0010] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (000+0) [0100] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (000+0) [1000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (001+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ba                                  { 0 } (010+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A00B000-0 As Ba                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A0G0000-0 As Ba                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_canonicalise_barren_worlds(self, starline):
        sector = Sector('# Core', '# 0, 0')
        star1 = None
        allowed_errors = [
            'Input UWP malformed'
        ]

        try:
            star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        except ValueError as e:
            rep = str(e)

            if rep in allowed_errors:
                pass
            else:
                raise e
        assume(star1 is not None)
        star1.index = 0
        star1.allegiance_base = 'NaHu'

        assume('0' == str(star1.pop) and 'Ba' in star1.tradeCode.codes)

        _, canonical_messages = star1.check_canonical()

        star1.canonicalise()

        _, nu_messages = star1.check_canonical()
        invalid = [item for item in nu_messages if ('should be 0 for barren worlds' in item or 'does not match' in item)]

        self.assertTrue(
            len(canonical_messages) >= len(nu_messages),
            'New canonical-check messages should not happen: \n' + starline
        )
        badline = '' if 0 == len(invalid) else invalid[0]
        self.assertEqual(0, len(invalid), 'At least one characteristic not canonicalised: \n' + starline + '\n' + badline)

    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000100-0 As As                                  { 0 } (001+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As As                                  { 0 } (010+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000400-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000400-0 As As                                  { 0 } (006+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000700-0 As As                                  { 0 } (00D+0) [0000] - - A 000 0 NaHu G5 V')
    def test_canonicalise_ex_on_non_barren_worlds(self, starline):
        sector = Sector('# Core', '# 0, 0')
        star1 = None
        allowed_errors = [
            'Input UWP malformed'
        ]

        try:
            star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        except ValueError as e:
            rep = str(e)
            if rep in allowed_errors:
                pass
            else:
                raise e
        assume(star1 is not None)
        star1.index = 0
        star1.allegiance_base = 'NaHu'

        assume(not '0' == str(star1.pop) and 'Ba' not in star1.tradeCode.codes)

        _, canonical_messages = star1.check_canonical()

        star1.canonicalise()

        _, nu_messages = star1.check_canonical()
        invalid = [item for item in nu_messages if (' - EX Calculated ' in item)]

        self.assertTrue(
            len(canonical_messages) >= len(nu_messages),
            'New canonical-check messages should not happen: \n' + starline
        )
        badline = '' if 0 == len(invalid) else invalid[0]
        self.assertEqual(0, len(invalid), 'At least one characteristic not canonicalised: \n' + starline + '\n' + badline)

    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))
    @example('0101 0                    A000100-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 Coruscant            A000F00-0 As As                                  { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As As                                  { 0 } (000+0) [7000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As As                                  { 0 } (000+0) [00F0] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A140620-9 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_canonicalise_cx_on_non_barren_worlds(self, starline):
        sector = Sector('# Core', '# 0, 0')
        star1 = None
        allowed_errors = [
            'Input UWP malformed'
        ]

        try:
            star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
        except ValueError as e:
            rep = str(e)
            if rep in allowed_errors:
                pass
            else:
                raise e
        assume(star1 is not None)
        star1.index = 0
        star1.allegiance_base = 'NaHu'

        assume(not '0' == str(star1.pop) and 'Ba' not in star1.tradeCode.codes)

        _, canonical_messages = star1.check_canonical()

        star1.canonicalise()

        _, nu_messages = star1.check_canonical()
        invalid = [item for item in nu_messages if (' - CX Calculated ' in item)]

        self.assertTrue(
            len(canonical_messages) >= len(nu_messages),
            'New canonical-check messages should not happen: \n' + starline
        )
        badline = '' if 0 == len(invalid) else invalid[0]
        self.assertEqual(0, len(invalid), 'At least one characteristic not canonicalised: \n' + starline + '\n' + badline)

    """
    Given a regex-matching string that results in a Star object when parsed, that Star should cleanly canonicalise
    """
    @given(mixed_starline())
    @settings(
        suppress_health_check=[HealthCheck(3), HealthCheck(2)],  # suppress slow-data health check, too-much filtering
        deadline=timedelta(1000))
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   00 D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00 D')
    @example('0101 000000000000000 A000200-0 000000000000000 {0} -  [0000] - - 0 000   00 D')
    @example('0101 000000000000000 A000a00-0 000000000000000 {0} (000-0) [0000] - - 0 000   00 D')
    @example('0101 000000000000000 A000Z00-0 000000000000000 {0} (000-0) [0000] - - 0 000   00 D')
    @example('2123 Medurma              A9D7954-C Hi An Cs Di(Miyavine) Asla1 S\'mr0     { 3 }  (G8E+1) [7C3A] BEF  -  - 823 12 ImDv G0 V            Xb:1823 Xb:1926 Xb:2223 Xb:2225 Xb:2322')
    @example('0101 0                    A000400-0 As Ba                                  { 0 } (001+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Cp Cp Cp Cp Cp Cp Cp Cp Cp Cp          { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000600-0 Cp Cx Cs Mr Da RsA RsB RsG             { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000600-0 Cp Cx Cs Mr Da RsA                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-C As Lo Va                              { 1 }  (001+1) [1217] B    -  A 000 0  NaHu G5 V')
    @example('0101 0                    A000100-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A000900-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As Ri                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A244500-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As As                                  { 0 } (001+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A244500-0 As As O:0101                           { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 0                    A244500-0 As As C:0101                           { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    @example('0101 000000000000000 ???????-? 000000000000000       - - A 000 0 00')
    @example('0101 000000000000000 ???????-? 000000000000000 - -  [0001] B - A 000   00')
    @example('0101 0                    A201000-0 As As                                  { 0 } (000+0) [0000] B - A 000 0 NaHu G5 V')
    def test_canonicalise_from_regex_match_and_verify_idempotency(self, starline):
        assume('00' != starline[0:2] and '00' != starline[2:4])
        assume(33 > int(starline[0:2]) and 41 > int(starline[2:4]))

        sector = Sector('# Core', '# 0, 0')
        foo = None

        with contextlib.suppress(ValueError):
            foo = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')

        assume(foo is not None)

        foo.index = 0
        foo.allegiance_base = 'NaHu'

        self.assertIsNotNone(foo._hash, "Hash not calculated for original star")
        well_formed = foo.is_well_formed()
        assume(well_formed)

        foo.canonicalise()
        _, nu_messages = foo.check_canonical()  # Should be in canonical form after canonicalise call

        badline = '' if 0 == len(nu_messages) else nu_messages[0]
        self.assertEqual(0, len(nu_messages), 'At least one characteristic not canonicalised: \n' + starline + '\n' + badline)

        # Now verify canonicalisation is idempotent on resulting string
        first_round = foo.parse_to_line()
        nu_foo = DeltaStar.parse_line_into_star(first_round, sector, 'fixed', 'fixed')
        self.assertIsNotNone(nu_foo, "Canonicalised line should parse cleanly")
        nu_foo.canonicalise()

        _, nu_messages = nu_foo.check_canonical()  # Should be in canonical form after canonicalise call

        badline = '' if 0 == len(nu_messages) else nu_messages[0]
        self.assertEqual(0, len(nu_messages), 'At least one characteristic not canonicalised: \n' + starline + '\n' + badline)

        second_round = nu_foo.parse_to_line()
        self.assertEqual(first_round, second_round, 'Canonicalisation should be idempotent.\nHypothesis input: ' + starline + '\n')


if __name__ == '__main__':
    unittest.main()

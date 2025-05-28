"""
Created on 19 Apr, 2025

@author: CyberiaResurrection
"""
import copy
import logging

from PyRoute import Star
from PyRoute.AreaItems.Sector import Sector
from Tests.baseTest import baseTest


class testStarParsingImpliedTradeCodes(baseTest):

    def testParseImpliedVaGivenAsTradeCode(self):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Core', '# 0, 0')

        starline = "1903 Waypoint             C000322-C As Lo Ht                       { 0 }  (720-4) [1318] -    -  - 202 14 SoCf M3 V          "

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry'
                )
                inner_logger.debug(
                    'Dummy log entry'
                )

                star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = "So"

                self.assertTrue(star1.is_well_formed())

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                self.assertEqual(4, len(star1.tradeCode.codes), "Unexpected number of trade codes")
                no_match = 'Calculated "Va" not in trade codes'
                for line in output:
                    self.assertTrue(no_match not in line, "Va trade code not added during parsing")

    def testParseImpliedHiGivenInTradeCode(self):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Core', '# 0, 0')

        starline = "0110 Rruezugzal           A843A7B-E In Po                               - K  - 703   Va F2 V M7 V F3 V M4 V"

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry'
                )
                inner_logger.debug(
                    'Dummy log entry'
                )

                star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = "So"

                self.assertTrue(star1.is_well_formed())

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                self.assertEqual(3, len(star1.tradeCode.codes), "Unexpected number of trade codes")
                no_match = 'Calculated "Hi" not in trade codes'
                for line in output:
                    self.assertTrue(no_match not in line, "Hi trade code not added during parsing")

    def testParsePresentVaGivenAsTradeCode(self):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Core', '# 0, 0')

        starline = "1903 Waypoint             C000322-C As Lo Ht Va                    { 0 }  (720-4) [1318] -    -  - 202 14 SoCf M3 V          "

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry'
                )
                inner_logger.debug(
                    'Dummy log entry'
                )

                star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = "So"

                self.assertTrue(star1.is_well_formed())

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                self.assertEqual(4, len(star1.tradeCode.codes), "Unexpected number of trade codes")
                no_match = 'Calculated "Va" not in trade codes'
                for line in output:
                    self.assertTrue(no_match not in line, "Va trade code not added during parsing")

    def testParsePresentHiGivenInTradeCode(self):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Core', '# 0, 0')

        starline = "0110 Rruezugzal           A843A7B-E In Po Hi                            - K  - 703   Va F2 V M7 V F3 V M4 V"

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry'
                )
                inner_logger.debug(
                    'Dummy log entry'
                )

                star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = "So"

                self.assertTrue(star1.is_well_formed())

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                self.assertEqual(3, len(star1.tradeCode.codes), "Unexpected number of trade codes")
                no_match = 'Calculated "Hi" not in trade codes'
                for line in output:
                    self.assertTrue(no_match not in line, "Hi trade code not added during parsing")

    def test_dont_double_missing_trade_code_warnings(self):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)
        inner_logger.manager.disable = 0
        inner_logger.setLevel(10)

        sector = Sector('# Amderstun', '# 0,-6')

        starline = "2322 Teneslis             A9978CA-B                                     - KM A 413   Am        "

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            self.assertTrue(outer_logger.isEnabledFor(10), "Outer logger disabled for DEBUG")
            self.assertTrue(inner_logger.isEnabledFor(10), "Inner logger disabled for DEBUG")

            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                outer_logger.debug(
                    'Dummy log entry'
                )
                inner_logger.debug(
                    'Dummy log entry'
                )

                star1 = Star.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                star1.index = 0
                star1.allegiance_base = "Am"

                self.assertTrue(star1.is_well_formed())

                output = copy.deepcopy(outer_logs.output)
                output.extend(inner_logs.output)
                self.assertTrue(0 < len(output), "At least one log message expected")
                logset = set(output)
                self.assertEqual(len(logset), len(output), "At least one log line duplicated")

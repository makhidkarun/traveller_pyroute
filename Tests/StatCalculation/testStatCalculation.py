"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
import copy
import logging
from unittest.mock import MagicMock

from PyRoute import ObjectStatistics, Star
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary
from PyRoute.StatCalculation.StatCalculation import StatCalculation
from PyRoute.StatCalculation.UWPCollection import UWPCollection
from PyRoute.Utilities.NoNoneDefaultDict import NoNoneDefaultDict
from Tests.baseTest import baseTest


class testStatCalculation(baseTest):

    def test_init(self) -> None:
        galaxy = Galaxy(8, 4)

        stat = StatCalculation(galaxy)
        logger = stat.logger
        self.assertEqual('PyRoute.StatCalculation', logger.name)

        self.assertIsInstance(stat.galaxy, Galaxy)
        self.assertIsInstance(stat.all_uwp, UWPCollection)
        self.assertIsInstance(stat.imp_uwp, UWPCollection)

    def test_add_pop_to_sophont_1(self) -> None:
        galaxy = Galaxy(8, 4)

        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        self.assertEqual(0, objstat.populations["Huma"].population)
        stat.add_pop_to_sophont(objstat, star1)
        self.assertEqual(10, objstat.populations["Huma"].population)

        star2 = Star.parse_line_into_star(
            "0104 Irkigkhan            C9C4833-9 Dolp4 Asla6  FoobX   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        self.assertEqual(0, objstat.populations["Dolp"].population)
        self.assertEqual(0, objstat.populations["Asla"].population)
        self.assertEqual(0, objstat.populations["Foob"].population)
        stat.add_pop_to_sophont(objstat, star2)
        self.assertEqual(40, objstat.populations["Dolp"].population)
        self.assertEqual(60, objstat.populations["Asla"].population)
        self.assertEqual(-1, objstat.populations["Foob"].population)

        star3 = Star.parse_line_into_star(
            "0105 Irkigkhan            C9C4833-9 [VargW]         { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        self.assertEqual(0, objstat.populations["Varg"].population)
        stat.add_pop_to_sophont(objstat, star3)
        self.assertEqual(100, objstat.populations["Varg"].population)

        star4 = Star.parse_line_into_star(
            "0106 Irkigkhan            C9C4833-9 Geon? Zoid0 VargA { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        self.assertEqual(0, objstat.populations["Geon"].population)
        self.assertEqual(0, objstat.populations["Zoid"].population)
        self.assertEqual(100, objstat.populations["Varg"].population)
        stat.add_pop_to_sophont(objstat, star4)
        self.assertEqual(0, objstat.populations["Geon"].population)
        self.assertEqual(5, objstat.populations["Zoid"].population)
        self.assertEqual(100, objstat.populations["Varg"].population)

        self.assertEqual([], objstat.populations['Huma'].homeworlds)
        self.assertEqual([], objstat.populations['Dolp'].homeworlds)
        self.assertEqual([], objstat.populations['Asla'].homeworlds)
        self.assertEqual([star3], objstat.populations['Varg'].homeworlds)
        self.assertEqual([], objstat.populations['Geon'].homeworlds)
        self.assertEqual([], objstat.populations['Zoid'].homeworlds)
        self.assertEqual([], objstat.populations['Foob'].homeworlds)

    def test_add_pop_to_sophont_2(self) -> None:
        outer_logger = logging.getLogger('PyRoute.StatCalculation')
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

        galaxy = Galaxy(8, 4)

        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl Huma9 Dolp1 Asla1             { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Woop Woop            C9C4733-9 Fl Huma9 Dolp1 Asla0             { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            stat.add_pop_to_sophont(objstat, star1)
            stat.add_pop_to_sophont(objstat, star2)
            stat.add_pop_to_sophont(objstat, star1)
            stat.add_pop_to_sophont(objstat, star2)

        expected = [
            'WARNING:PyRoute.StatCalculation:Irkigkhan (Core 0103) has sophont percent over 100%: -10.0',
            'INFO:PyRoute.StatCalculation:Woop Woop (Core 0104) has a sophont percent just over 100%: -5.0'
        ]
        actual = copy.deepcopy(outer_logs.output)
        self.assertEqual(expected, actual)
        self.assertTrue(star1.suppress_soph_percent_warning)
        self.assertTrue(star2.suppress_soph_percent_warning)

    def test_add_stats_1(self) -> None:
        galaxy = Galaxy(8, 4)

        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl (Zoid)             { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.tradeIn = 200
        star1.tradeOver = 200
        star1.passIn = 11
        star1.eti_cargo_volume = 1
        star1.eti_pass_volume = 1

        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')
        star2.eti_pass_volume = 0
        star2.eti_cargo_volume = 3

        star3 = Star.parse_line_into_star(
            "0105 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')
        star3.eti_pass_volume = 1
        star3.eti_cargo_volume = 0

        star4 = Star.parse_line_into_star(
            "0106 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')
        star4.eti_pass_volume = 0
        star4.eti_cargo_volume = 1

        stat.add_stats(objstat, star1)
        self.assertEqual(40, objstat.population)
        self.assertEqual(117, objstat.economy)
        self.assertEqual(1, objstat.number)
        self.assertEqual(756, objstat.sum_ru)
        self.assertEqual(400, objstat.tradeVol)
        self.assertEqual(1.5, objstat.col_be)
        self.assertAlmostEquals(0.45, objstat.im_be, 3)
        self.assertEqual(11, objstat.passengers)
        self.assertEqual(0, objstat.spa_people)
        self.assertEqual(1, objstat.port_size['B'])
        self.assertEqual(1, objstat.port_size[star1.starportSize])
        self.assertEqual(1, objstat.code_counts['Fl'])
        self.assertEqual(1, objstat.gg_count)
        self.assertEqual(8, objstat.worlds)
        self.assertEqual(1, objstat.stars)
        self.assertEqual(1, objstat.star_count[1])
        self.assertEqual(1, objstat.primary_count['M'])
        self.assertEqual(1, objstat.eti_worlds)
        self.assertEqual(1, objstat.eti_cargo)
        self.assertEqual(1, objstat.eti_pass)
        self.assertEqual([star1], objstat.homeworlds)
        stat.add_stats(objstat, star2)
        self.assertEqual(2, objstat.eti_worlds)
        self.assertEqual(4, objstat.eti_cargo)
        self.assertEqual(1, objstat.eti_pass)
        stat.add_stats(objstat, star3)
        self.assertEqual(3, objstat.eti_worlds)
        self.assertEqual(4, objstat.eti_cargo)
        self.assertEqual(2, objstat.eti_pass)
        stat.add_stats(objstat, star4)
        self.assertEqual(4, objstat.eti_worlds)
        self.assertEqual(5, objstat.eti_cargo)
        self.assertEqual(2, objstat.eti_pass)

    def test_add_stats_2(self) -> None:
        galaxy = Galaxy(8, 4)

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        cases = [
            ('A', ['Naval base', 'Scout base']),
            ('B', ['Naval base', 'Way station']),
            ('C', ['Corsair base']),
            ('F', ['Naval base', 'Military base']),
            ('H', ['Corsair base', 'Naval base']),
            ('U', ['Tlaukhu base', 'Clan base']),
            ('Z', ['Naval base', 'Military base'])
        ]

        for base_type, mappings in cases:
            with self.subTest('base_type'):
                star1.baseCode = base_type

                stat = StatCalculation(galaxy)
                objstat = ObjectStatistics()

                stat.add_stats(objstat, star1)
                stat.add_stats(objstat, star1)
                for mapp in mappings:
                    self.assertEqual(2, objstat.bases[mapp])

    def test_add_stats_3(self) -> None:
        galaxy = Galaxy(8, 4)

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()
        objstat.primary_count[None] = 0

        msg = None
        try:
            stat.add_stats(objstat, star1)
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Null primary type will blow up templating', msg)

    def test_max_tl_1(self) -> None:
        galaxy = Galaxy(8, 4)

        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')

        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()

        self.assertEqual(0, objstat.maxTL)
        self.assertEqual('X', objstat.maxPort)
        self.assertEqual(0, objstat.maxPop)
        stat.max_tl(objstat, star2)
        self.assertEqual(7, objstat.maxTL)
        self.assertEqual('E', objstat.maxPort)
        self.assertEqual(1, objstat.maxPop)
        stat.max_tl(objstat, star1)
        self.assertEqual(9, objstat.maxTL)
        self.assertEqual('B', objstat.maxPort)
        self.assertEqual(7, objstat.maxPop)

    def test_per_capita_1(self) -> None:
        cases = [
            (100001, 2000000, 2000001, 19999, 2),
            (100001, 2000000, 1000001, 19999, 1),
            (100000, 2000000, 1000000, 20000, 0),
            (99999, 2000000, 1000000, 20000, 0),
            (1, 10, 0, 10000, 0),
            (0, 200000, 1000000, 0, 0)
        ]
        galaxy = Galaxy(8, 4)
        for pop, econ, shipyd, exp_percapita, exp_shipyd in cases:
            with self.subTest(str(pop) + " " + str(econ) + " " + str(shipyd)):
                stat = StatCalculation(galaxy)
                objstat = ObjectStatistics()
                objstat.population = pop
                objstat.economy = econ
                objstat.shipyards = shipyd
                stat.per_capita([], objstat)
                self.assertEqual(exp_percapita, objstat.percapita)
                self.assertEqual(exp_shipyd, objstat.shipyards)

    def test_per_capita_2(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Irkigkhan            B9C4733-7 Fl                   { 0 }  (E69+0) [4726]  B    - - 223 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star3 = Star.parse_line_into_star(
            "0105 Irkigkhan            B9C4833-A Fl Cp                { 0 }  (E69+0) [4726]  B    - - 223 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star4 = Star.parse_line_into_star(
            "0106 Irkigkhan            B9C4833-8 Fl Cs                { 0 }  (E69+0) [4726]  B    - - 323 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(8, 4)
        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()
        objstat.maxTL = 10
        objstat.maxPop = 8

        stat.per_capita([star1, star2, star3, star4], objstat)
        self.assertEqual(8.5, objstat.TLmean)
        self.assertAlmostEquals(1.118, objstat.TLstddev, 3)
        self.assertEqual([star4, star3], objstat.high_pop_worlds)
        self.assertEqual([star3], objstat.high_tech_worlds)
        self.assertEqual([star3], objstat.subsectorCp)
        self.assertEqual([star4], objstat.sectorCp)
        self.assertEqual([], objstat.otherCp)

    def test_per_capita_3(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726]  B    - - 423 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Irkigkhan            B9C4733-7 Fl                   { 0 }  (E69+0) [4726]  B    - - 223 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star3 = Star.parse_line_into_star(
            "0105 Irkigkhan            B9C4833-A Fl Cp                { 0 }  (E69+0) [4726]  B    - - 223 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(8, 4)
        stat = StatCalculation(galaxy)
        objstat = ObjectStatistics()
        objstat.maxTL = 10
        objstat.maxPop = 8

        stat.per_capita([star1, star2, star3], objstat)
        self.assertEqual(0, objstat.TLmean)
        self.assertAlmostEquals(0, objstat.TLstddev, 3)
        self.assertEqual([star3], objstat.high_pop_worlds)
        self.assertEqual([star3], objstat.high_tech_worlds)
        self.assertEqual([star3], objstat.subsectorCp)
        self.assertEqual([], objstat.sectorCp)
        self.assertEqual([], objstat.otherCp)

    def test_write_statistics(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 15, 1, False)

        statcalc = StatCalculation(galaxy)
        statcalc.logger.manager.disable = 0

        exp_logs = [
            'INFO:PyRoute.StatCalculation:Charted star count: 0',
            'INFO:PyRoute.StatCalculation:Charted population 0',
            'DEBUG:PyRoute.StatCalculation:Sector Zarushagar star count: 0',
            'DEBUG:PyRoute.StatCalculation:Allegiance Third Imperium, Domain of Ilelish (ImDi: base False -> Im) star count: 0',
            'DEBUG:PyRoute.StatCalculation:Allegiance Unknown Allegiance (Im: base True) star count: 0',
            'DEBUG:PyRoute.StatCalculation:min count: 0, match: 0'
        ]
        self.assertEqual(0, statcalc.logger.manager.disable)

        with self.assertLogs(statcalc.logger, 'DEBUG') as outer_logs:
            statcalc._write_statistics_to_wiki = MagicMock(name="_write_statistics_to_wiki")
            statcalc.write_statistics(0, 0, {})

            output = copy.deepcopy(outer_logs.output)
            self.assertEqual(exp_logs, output)
            statcalc._write_statistics_to_wiki.assert_called_once_with(0, 0, {})

    def test_calculate_statistics(self) -> None:
        filename = 'DeltaFiles/Zarushagar-Ibara.sec'
        sourcefile = self.unpack_filename(filename)

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta['Dagudashaag'] = SectorDictionary('Dagudashaag', '')
        delta['Dagudashaag'].position = '# 0, 0'
        delta[sector.name] = sector

        galaxy = DeltaGalaxy(15, 4)
        galaxy.read_sectors(delta, "scaled", "scaled", 10, "trade", 12, 1, False)
        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

        statcalc = StatCalculation(galaxy)
        statcalc.logger.manager.disable = 0

        exp_logs = [
            'INFO:PyRoute.StatCalculation:Calculating statistics for 37 worlds'
        ]
        high_pop_star = galaxy.stars.nodes[34]['star']

        with self.assertLogs(statcalc.logger, 'DEBUG') as outer_logs:
            statcalc.calculate_statistics(True)
            output = copy.deepcopy(outer_logs.output)
            self.assertEqual(exp_logs, output)

        exp_port_size = NoNoneDefaultDict(int)
        exp_port_size[0] = 8
        exp_port_size[2] = 4
        exp_port_size[3] = 10
        exp_port_size[4] = 9
        exp_port_size[5] = 6
        exp_port_size['A'] = 6
        exp_port_size['B'] = 22
        exp_port_size['C'] = 4
        exp_port_size['D'] = 3
        exp_port_size['E'] = 2

        exp_code_count = NoNoneDefaultDict(int)
        exp_code_count['Ag'] = 5
        exp_code_count['Cp'] = 1
        exp_code_count['Da'] = 2
        exp_code_count['De'] = 1
        exp_code_count['Fl'] = 1
        exp_code_count['Ga'] = 5
        exp_code_count['He'] = 5
        exp_code_count['Hi'] = 3
        exp_code_count['Ic'] = 3
        exp_code_count['In'] = 2
        exp_code_count['Lo'] = 13
        exp_code_count['Mr'] = 2
        exp_code_count['Na'] = 7
        exp_code_count['Ni'] = 13
        exp_code_count['O:0804'] = 1
        exp_code_count['Pa'] = 2
        exp_code_count['Ph'] = 4
        exp_code_count['Pi'] = 5
        exp_code_count['Po'] = 9
        exp_code_count['Pr'] = 1
        exp_code_count['Pz'] = 5
        exp_code_count['Ri'] = 2
        exp_code_count['TentW'] = 2
        exp_code_count['Va'] = 6

        exp_star_count = NoNoneDefaultDict(int)
        exp_star_count[1] = 23
        exp_star_count[2] = 14

        exp_primary_count = NoNoneDefaultDict(int)
        exp_primary_count['K'] = 12
        exp_primary_count['M'] = 10
        exp_primary_count['A'] = 1
        exp_primary_count['G'] = 9
        exp_primary_count['F'] = 5

        galstat = galaxy.stats

        self.assertEqual(20312, galstat.population)
        self.assertEqual(100376, galstat.economy)
        self.assertEqual(37, galstat.number)
        self.assertEqual(38046, galstat.sum_ru)
        self.assertEqual(221650000000, galstat.tradeVol)
        self.assertEqual(3178.4, galstat.col_be)
        self.assertAlmostEqual(1135.98, galstat.im_be, 3)
        self.assertEqual(14776500, galstat.passengers)
        self.assertEqual(44300, galstat.spa_people)
        self.assertEqual(exp_port_size, galstat.port_size)
        self.assertEqual(exp_code_count, galstat.code_counts)
        self.assertEqual(35, galstat.gg_count)
        self.assertEqual(383, galstat.worlds)
        self.assertEqual(51, galstat.stars)
        self.assertEqual(exp_star_count, galstat.star_count)
        self.assertEqual(exp_primary_count, galstat.primary_count)
        self.assertEqual(0, galstat.eti_worlds)
        self.assertEqual(0, galstat.eti_cargo)
        self.assertEqual(0, galstat.eti_pass)
        self.assertEqual([], galstat.homeworlds)

        self.assertEqual(galstat.__dict__, galaxy.sectors['Zarushagar'].stats.__dict__)
        self.assertEqual([high_pop_star], galaxy.sectors['Zarushagar'].stats.high_pop_worlds)
        self.assertEqual(galstat.__dict__, galaxy.sectors['Zarushagar'].subsectors['A'].stats.__dict__)
        self.assertEqual([high_pop_star], galaxy.sectors['Zarushagar'].subsectors['A'].stats.high_pop_worlds)
        expected_starport_budgets = {0: 34.0, 1: 0, 2: 92.0, 3: 102.0, 4: 14.0, 5: 118.0, 6: 20.0, 7: 6.0, 8: 208.0,
                                     9: 279.0, 10: 0, 11: 219.0, 12: 0, 13: 1.0, 14: 4.0, 15: 53.0, 16: 0, 17: 1409.0,
                                     18: 1435.0, 19: 0, 20: 25.0, 21: 0, 22: 93.0, 23: 20.0, 24: 781.0, 25: 0,
                                     26: 1854.0, 27: 8.0, 28: 0, 29: 0, 30: 0, 31: 1.0, 32: 13.0, 33: 7.0, 34: 1298.0,
                                     35: 766.0, 36: 0}
        expected_starport_sizes = {0: 4, 1: 2, 2: 4, 3: 4, 4: 3, 5: 4, 6: 3, 7: 3, 8: 4, 9: 4, 10: 0, 11: 4, 12: 2,
                                   13: 3, 14: 3, 15: 4, 16: 0, 17: 5, 18: 5, 19: 0, 20: 3, 21: 0, 22: 4, 23: 3, 24: 5,
                                   25: 0, 26: 5, 27: 3, 28: 2, 29: 0, 30: 0, 31: 2, 32: 3, 33: 3, 34: 5, 35: 5, 36: 0}
        for starnum in expected_starport_budgets:
            budget_star = galaxy.stars.nodes[starnum]['star']
            self.assertEqual(expected_starport_budgets[starnum], budget_star.starportBudget,
                             str(starnum) + " budget")
            self.assertEqual(expected_starport_sizes[starnum], budget_star.uwpCodes['Starport Size'],
                             str(starnum) + " size")

        imp_stats = statcalc.imp_uwp
        self.assertEqual(25, imp_stats.uwp['Starport']['A'].population, 'A port')
        self.assertEqual(18827, imp_stats.uwp['Starport']['B'].population, 'B port')
        self.assertEqual(1360, imp_stats.uwp['Starport']['C'].population, 'C port')
        self.assertEqual(100, imp_stats.uwp['Starport']['D'].population, 'D port')
        self.assertEqual(0, imp_stats.uwp['Starport']['E'].population, 'E port')

        all_stats = statcalc.all_uwp
        self.assertEqual(25, all_stats.uwp['Starport']['A'].population, 'A port')
        self.assertEqual(18827, all_stats.uwp['Starport']['B'].population, 'B port')
        self.assertEqual(1360, all_stats.uwp['Starport']['C'].population, 'C port')
        self.assertEqual(100, all_stats.uwp['Starport']['D'].population, 'D port')
        self.assertEqual(0, all_stats.uwp['Starport']['E'].population, 'E port')

        self.assertEqual(1, len(galaxy.sectors['Zarushagar'].alg_sorted))
        self.assertEqual('Im', galaxy.sectors['Zarushagar'].alg_sorted[0].code)

        imdi_stats = galaxy.alg['ImDi'].stats
        self.assertEqual(0, imdi_stats.percapita)
        self.assertEqual(20312, imdi_stats.population)
        self.assertAlmostEqual(0, imdi_stats.TLmean, 1)
        self.assertAlmostEqual(0, imdi_stats.TLstddev, 1)
        self.assertEqual([], imdi_stats.high_pop_worlds)

        im_stats = galaxy.alg['Im'].stats
        self.assertEqual(4941, im_stats.percapita)
        self.assertEqual(20312, im_stats.population)
        self.assertEqual(20312, im_stats.population)
        self.assertAlmostEqual(10.5, im_stats.TLmean, 1)
        self.assertAlmostEqual(1.9, im_stats.TLstddev, 1)
        self.assertEqual([high_pop_star], im_stats.high_pop_worlds)

        im_stats = galaxy.sectors['Zarushagar'].alg['Im'].stats
        self.assertEqual(4941, im_stats.percapita)
        self.assertEqual(20312, im_stats.population)
        self.assertEqual(20312, im_stats.population)
        self.assertAlmostEqual(10.5, im_stats.TLmean, 1)
        self.assertAlmostEqual(1.9, im_stats.TLstddev, 1)
        self.assertEqual([high_pop_star], im_stats.high_pop_worlds)

        im_stats = galaxy.sectors['Zarushagar'].subsectors['A'].alg['Im'].stats
        self.assertEqual(4941, im_stats.percapita)
        self.assertEqual(20312, im_stats.population)
        self.assertEqual(20312, im_stats.population)
        self.assertAlmostEqual(10.5, im_stats.TLmean, 1)
        self.assertAlmostEqual(1.9, im_stats.TLstddev, 1)
        self.assertEqual([high_pop_star], im_stats.high_pop_worlds)

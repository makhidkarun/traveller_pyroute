"""
Created on Nov 30, 2021

@author: CyberiaResurrection
"""
from unittest.mock import patch

from PyRoute import Star
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.Calculation.CommCalculation import CommCalculation
from PyRoute.Calculation.NoneCalculation import NoneCalculation
from PyRoute.Calculation.OwnedWorldCalculation import OwnedWorldCalculation
from PyRoute.Calculation.TradeCalculation import TradeCalculation
from PyRoute.Calculation.TradeMPCalculation import TradeMPCalculation
from PyRoute.Calculation.XRouteCalculation import XRouteCalculation
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.RouteLandmarkGraph import RouteLandmarkGraph
from PyRoute.StatCalculation import ObjectStatistics
from Tests.baseTest import baseTest


class testGalaxy(baseTest):

    def setUp(self) -> None:
        self.reset_logging()

    def test_init_blank(self) -> None:
        galaxy = Galaxy(8)
        self.assertEqual('PyRoute.Galaxy', galaxy.logger.name)
        self.assertEqual({}, galaxy.sectors)
        self.assertEqual('[[Charted Space]]', galaxy.borders.galaxy._wiki_name)

    def test_get_state(self) -> None:
        galaxy = Galaxy(0)
        exp_dict = {
            '_wiki_name': '[[Charted Space]]',
            'alg': {},
            'big_component': None,
            'debug_flag': False,
            'historic_costs': None,
            'max_jump_range': 4,
            'min_btn': 0,
            'name': 'Charted Space',
            'output_path': 'maps',
            'star_mapping': {},
            'stats': ObjectStatistics(),
            'worlds': []
        }
        self.assertEqual(exp_dict, galaxy.__getstate__())

    def test_is_well_formed(self) -> None:
        galaxy = Galaxy(0)
        galaxy.is_well_formed()

    """
    A very simple, barebones test to check that Verge and Reft end up in their correct relative positions
    - Verge being immediately rimward of Reft
    """
    def testVerticalOrdering(self) -> None:
        galaxy = Galaxy(0)

        reft = Sector("# Reft", "# -3, 0")
        self.assertEqual(-3, reft.x)
        self.assertEqual(0, reft.y)

        verge = Sector("# Verge", "# -3, -1")
        self.assertEqual(-3, verge.x)
        self.assertEqual(-1, verge.y)

        galaxy.sectors[reft.name] = reft
        galaxy.sectors[verge.name] = verge

        # verify, before bounding sectors gets run, nothing is hooked up
        self.assertIsNone(galaxy.sectors[reft.name].coreward)
        self.assertIsNone(galaxy.sectors[reft.name].rimward)
        self.assertIsNone(galaxy.sectors[reft.name].spinward)
        self.assertIsNone(galaxy.sectors[reft.name].trailing)
        self.assertIsNone(galaxy.sectors[verge.name].coreward)
        self.assertIsNone(galaxy.sectors[verge.name].rimward)
        self.assertIsNone(galaxy.sectors[verge.name].spinward)
        self.assertIsNone(galaxy.sectors[verge.name].trailing)

        # set bounding sectors
        galaxy.set_bounding_sectors()

        # now assert that Reft is coreward from Verge, and (likewise), Verge is rimward from Reft, and nothing else
        # got set
        self.assertEqual(galaxy.sectors[reft.name], galaxy.sectors[verge.name].coreward, "Reft should be coreward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].rimward, "Nothing should be rimward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].spinward, "Nothing should be spinward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].trailing, "Nothing should be trailing of Verge")
        self.assertIsNone(galaxy.sectors[reft.name].coreward, "Nothing should be coreward of Reft")
        self.assertIsNone(galaxy.sectors[reft.name].trailing, "Nothing should be trailing of Reft")
        self.assertIsNone(galaxy.sectors[reft.name].spinward, "Nothing should be spinward of Reft")
        self.assertEqual(galaxy.sectors[verge.name], galaxy.sectors[reft.name].rimward, "Verge should be rimward of Reft")

    """
    A very simple, barebones test to check that Dagudashaag and Core end up in their correct relative positions
    - Dagudashaag being immediately spinward of Core
    """
    def testHorizontalOrdering(self) -> None:
        galaxy = Galaxy(0)

        core = Sector("# Core", "# 0, 0")
        self.assertEqual(0, core.x)
        self.assertEqual(0, core.y)

        dagudashaag = Sector("# Dagudashaag", "# -1, 0")
        self.assertEqual(-1, dagudashaag.x)
        self.assertEqual(0, dagudashaag.y)

        galaxy.sectors[core.name] = core
        galaxy.sectors[dagudashaag.name] = dagudashaag

        # verify, before bounding sectors gets run, nothing is hooked up
        self.assertIsNone(galaxy.sectors[core.name].coreward)
        self.assertIsNone(galaxy.sectors[core.name].rimward)
        self.assertIsNone(galaxy.sectors[core.name].spinward)
        self.assertIsNone(galaxy.sectors[core.name].trailing)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].coreward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].rimward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].spinward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].trailing)

        # set bounding sectors
        galaxy.set_bounding_sectors()

        # now assert that Dagudashaag is spinward from Core, Core is trailing of Dagudashaag, and nothing else
        # got set
        self.assertEqual(galaxy.sectors[dagudashaag.name], galaxy.sectors[core.name].spinward, "Dagudashaag should be spinward of core")
        self.assertIsNone(galaxy.sectors[core.name].coreward, "Nothing should be coreward of Core")
        self.assertIsNone(galaxy.sectors[core.name].rimward, "Nothing should be rimward of Core")
        self.assertIsNone(galaxy.sectors[core.name].trailing, "Nothing should be trailing of core")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].coreward, "Nothing should be coreward of Dagudashaag")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].rimward, "Nothing should be rimward of Dagudashaag")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].spinward, "Nothing should be spinward of Dagudashaag")
        self.assertEqual(galaxy.sectors[core.name], galaxy.sectors[dagudashaag.name].trailing, "Core should be trailing of Dagudashaag")

    def test_add_star_to_galaxy(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        subs = Subsector('Foobar', 'A', sector)
        sector.subsectors['A'] = subs
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(0)
        galaxy.trade = NoneCalculation(galaxy)
        galaxy.sectors['Core'] = sector
        final = galaxy.add_star_to_galaxy(star1, 1, sector)
        self.assertEqual(2, final)
        galaxy.set_positions()
        self.assertIsInstance(galaxy.historic_costs, RouteLandmarkGraph)

    def test_process_eti(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        subs = Subsector('Foobar', 'A', sector)
        sector.subsectors['A'] = subs
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(0)
        galaxy.trade = NoneCalculation(galaxy)
        galaxy.sectors['Core'] = sector
        galaxy.add_star_to_galaxy(star1, 1, sector)
        galaxy.add_star_to_galaxy(star2, 2, sector)
        galaxy.stars.add_edge(1, 2, btn=0)
        galaxy.process_eti()
        edge = galaxy.stars.get_edge_data(1, 2)
        self.assertEqual(0, edge['CargoTradeIndex'])
        self.assertEqual(0, edge['PassTradeIndex'])

    def test_set_trade_object(self) -> None:
        cases = [
            ('trade', TradeCalculation, 10),
            ('trade-mp', TradeMPCalculation, 10),
            ('comm', CommCalculation, 10),
            ('xroute', XRouteCalculation, 5),
            ('none', NoneCalculation, 10),
            ('owned', OwnedWorldCalculation, 10)
        ]

        for routes, exp_type, exp_reuse in cases:
            with self.subTest(routes):
                galaxy = Galaxy(8)
                galaxy._set_trade_object(10, routes, 8, 1, False)
                self.assertIsInstance(galaxy.trade, exp_type)
                galaxy._set_trade_object(10, routes, 8, 1, False)
                self.assertIsInstance(galaxy.trade, exp_type)
                self.assertEqual(exp_reuse, galaxy.trade.route_reuse)
                if 'trade_mp' == routes:
                    self.assertEqual(1, galaxy.trade.mp_threads)
                    self.assertEqual(8, galaxy.trade.route_btn)
                elif 'trade' == routes:
                    self.assertEqual(8, galaxy.trade.min_btn)

    def test_process_owned_worlds_1(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        args = self._make_args()
        args.routes = 'trade'
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.generate_routes()
        galaxy.output_path = args.output
        galaxy.set_borders(args.borders, args.ally_match)

        foostar = galaxy.star_mapping[24]
        foostar.ownedBy = 'Dagu-0'
        barstar = galaxy.star_mapping[23]
        barstar.ownedBy = 'Re'
        barstar = galaxy.star_mapping[22]
        barstar.ownedBy = 'Px'

        logger = galaxy.logger
        logger.manager.disable = 0
        exp_logs = [
            'DEBUG:PyRoute.Galaxy:Worlds Woden (Zarushagar 0306) is owned by Mr',
            'DEBUG:PyRoute.Galaxy:Worlds Villenuve (Zarushagar 0507) is owned by Px',
            'DEBUG:PyRoute.Galaxy:Worlds Toulon-Cadiz (Zarushagar 0510) is owned by Re',
            'DEBUG:PyRoute.Galaxy:World Aslungi (Zarushagar 0605)@(6,5) owned by Dagu - 0',
            'DEBUG:PyRoute.Galaxy:Worlds Aslungi (Zarushagar 0605) is owned by None',
            'DEBUG:PyRoute.Galaxy:Worlds Airvae (Zarushagar 0801) is owned by Mr',
            'DEBUG:PyRoute.Galaxy:Worlds Ginshe (Zarushagar 0805) is owned by Gishin (Zarushagar 0804)'
        ]

        with patch('builtins.open', create=True) as mock_file, self.assertLogs(logger, 'DEBUG') as logs:
            galaxy.process_owned_worlds()
            mock_file.assert_called()
            self.assertEqual(2, mock_file.call_count)
            exp_1 = args.output + "/owned-worlds-names.csv"
            exp_2 = args.output + "/owned-worlds-list.csv"
            mock_file.assert_any_call(exp_1, 'w+b', -1)
            mock_file.assert_any_call(exp_2, 'w+b', -1)

            self.assertEqual(exp_logs, logs.output)

        milrule = {
            11: [18, 17, 26, 9], 31: [34, 27]
        }
        owned = {
            35: (34, [34, 26, 18, 17]),
        }
        none_owned = {
            24: [34, 26, 18, 17]
        }
        re_owned = {
            23: [18, 26, 2, 3]
        }
        px_owned = {
            22: [18, 26, 17, 34]
        }

        for item in galaxy.star_mapping:
            worldstar = galaxy.star_mapping[item]
            if item in owned:
                self.assertIsInstance(worldstar.ownedBy, tuple, "OwnedBy not tuple for " + str(item))
                self.assertEqual(owned[item][0], worldstar.ownedBy[0].index, "Bad ownership index for " + str(item))
                check = [item.index for item in worldstar.ownedBy[1]]
                self.assertEqual(owned[item][1], check, 'Bad ownership choices for ' + str(item))
            elif item in milrule:
                self.assertIsInstance(worldstar.ownedBy, tuple, "OwnedBy not tuple for " + str(item))
                self.assertEqual('Mr', worldstar.ownedBy[0], "OwnedBy not Mr for " + str(item))
                check = [item.index for item in worldstar.ownedBy[1]]
                self.assertEqual(milrule[item], check, 'Bad ownership choices for ' + str(item))
            elif item in re_owned:
                self.assertIsInstance(worldstar.ownedBy, tuple, "OwnedBy not tuple for " + str(item))
                self.assertEqual('Re', worldstar.ownedBy[0], "OwnedBy not Re for " + str(item))
                check = [item.index for item in worldstar.ownedBy[1]]
                self.assertEqual(re_owned[item], check, 'Bad ownership choices for ' + str(item))
            elif item in px_owned:
                self.assertIsInstance(worldstar.ownedBy, tuple, "OwnedBy not tuple for " + str(item))
                self.assertEqual('Px', worldstar.ownedBy[0], "OwnedBy not Px for " + str(item))
                check = [item.index for item in worldstar.ownedBy[1]]
                self.assertEqual(px_owned[item], check, 'Bad ownership choices for ' + str(item))
            elif item in none_owned:
                self.assertIsInstance(worldstar.ownedBy, tuple, "OwnedBy not tuple for " + str(item))
                self.assertIsNone(worldstar.ownedBy[0], "OwnedBy not None for " + str(item))
                check = [item.index for item in worldstar.ownedBy[1]]
                self.assertEqual(none_owned[item], check, 'Bad ownership choices for ' + str(item))
            else:
                self.assertEqual(worldstar, worldstar.ownedBy, 'Bad ownership choices for ' + str(item))

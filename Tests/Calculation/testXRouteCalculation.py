"""
Created on Oct 17, 2025

@author: CyberiaResurrection
"""
from collections import defaultdict
from unittest.mock import patch

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.XRouteCalculation import XRouteCalculation
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
from PyRoute.Position.Hex import Hex
from PyRoute.SystemData.UWP import UWP
from PyRoute.SystemData.StarList import StarList
from PyRoute.Star import Star
from PyRoute.TradeCodes import TradeCodes
from Tests.baseTest import baseTest


class testXRouteCalculation(baseTest):

    def setUp(self) -> None:
        self.reset_logging()

    def test_init_1(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        self.assertEqual(5, calc.route_reuse)
        self.assertEqual(0.2, calc.epsilon)
        self.assertEqual([], calc.capital)
        self.assertEqual([], calc.secCapitals)
        self.assertEqual([], calc.subCapitals)

    def find_sector_capital_1(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        core = Sector('# Core', '# 0, 0')
        star = Star()
        star.name = 'Star'
        star.sector = core
        calc.secCapitals.append(star)

        actual = calc.find_sector_capital(core)
        self.assertIsInstance(actual, Star)
        self.assertEqual('Star', actual.name)

    def find_sector_capital_2(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        core = Sector('# Core', '# 0, 0')
        actual = calc.find_sector_capital(core)
        self.assertIsNone(actual)

    def test_find_nearest_capital_1(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        core = Sector('# Core', '# 0, 0')
        capital = Star()
        capital.name = 'Capital'
        capital.sector = core
        capital.hex = Hex(core, '2118')

        star = Star()
        star.name = 'Star'
        star.sector = core
        star.hex = Hex(core, '3240')

        expected = (capital, 28)
        actual = calc.find_nearest_capital(star, [capital])
        self.assertEqual(expected, actual)

    def test_find_nearest_capital_2(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        core = Sector('# Core', '# 0, 0')
        star = Star()
        star.name = 'Star'
        star.sector = core
        star.hex = Hex(core, '3240')

        expected = (None, 9999)
        actual = calc.find_nearest_capital(star, [])
        self.assertEqual(expected, actual)

    def test_find_nearest_capital_3(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        msg = None
        try:
            calc.find_nearest_capital(None, None)
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('World must be Star object', msg)

        star = Star()

        msg = None
        try:
            calc.find_nearest_capital(star, None)
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Capitals must be list', msg)

    def test_find_nearest_capital_4(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)

        core = Sector('# Core', '# 0, 0')
        star = Star()
        star.name = 'Star'
        star.sector = core
        star.hex = Hex(core, '3240')

        woopwoop = Sector('# Woop Woop', '# -312, 0')
        wwstar = Star()
        wwstar.name = 'Woop Woop'
        wwstar.sector = woopwoop
        wwstar.hex = Hex(woopwoop, '1740')

        self.assertEqual(9999, wwstar.distance(star))

        expected = (None, 9999)
        actual = calc.find_nearest_capital(star, [wwstar])
        self.assertEqual(expected, actual)

    def test_unilateral_filter_1(self) -> None:
        cases = [
            ('R', 'Im', True),
            ('F', 'Im', True),
            ('A', 'Im', False),
            ('-', 'Im', False),
            ('R', 'Zh', True),
            ('F', 'Zh', True),
            ('A', 'Zh', True),
            ('-', 'Zh', True),
        ]

        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        for zone, alleg, expected in cases:
            with self.subTest(zone + " " + alleg):
                star = Star()
                star.zone = zone
                star.alg_code = alleg

                actual = calc.unilateral_filter(star)
                self.assertEqual(expected, actual)

    def test_route_weight_1(self) -> None:
        cases = [
            ('C', 'R', True, True, '0101', '0105', 271),
            ('D', 'F', True, True, '0101', '0105', 296),
            ('E', 'R', True, True, '0101', '0105', 296),
            ('X', 'F', True, True, '0101', '0105', 296),
            ('?', 'F', True, True, '0101', '0105', 296),
            ('E', 'A', True, True, '0101', '0105', 246),
            ('B', 'A', True, True, '0101', '0105', 196),
            ('C', 'R', False, False, '0101', '0105', 146),
            ('D', 'F', False, False, '0101', '0105', 171),
            ('E', 'R', False, False, '0101', '0105', 171),
            ('X', 'F', False, False, '0101', '0105', 171),
            ('?', 'F', False, False, '0101', '0105', 171),
            ('E', 'A', False, False, '0101', '0105', 121),
            ('B', 'A', False, False, '0101', '0105', 71),
        ]

        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        sector = Sector('# Core', '# 0, 0')

        for a_port, a_zone, a_popcode, a_dss, a_hex, b_hex, expected in cases:
            with self.subTest(a_port + " " + a_zone):
                raw_uwp = 'A555555-8'
                neighbour = Star()
                neighbour.uwp = UWP(raw_uwp)
                neighbour.tradeCode = TradeCodes('')
                neighbour.hex = Hex(sector, b_hex)
                neighbour.importance = 1
                neighbour.baseCode = '-'
                neighbour.zone = '-'
                neighbour.ru = 0

                star = Star()
                if a_port:
                    raw_uwp = a_port + raw_uwp[1:]
                if a_popcode:
                    raw_uwp = raw_uwp[0:4] + '0' + raw_uwp[5:]
                star.uwp = UWP(raw_uwp)
                star.tradeCode = TradeCodes('')
                star.zone = a_zone
                star.deep_space_station = a_dss
                star.hex = Hex(sector, a_hex)
                star.importance = 2
                star.baseCode = '-'
                star.ru = 0
                self.assertEqual(expected, calc.route_weight(star, neighbour))
                self.assertEqual(expected, calc.route_weight(neighbour, star))

    def test_route_weight_2(self) -> None:
        cases = [
            ('W', True, True, False, '0101', '0104', 58),
            ('N', True, False, True, '0101', '0104', 61),
            ('S', False, True, True, '0101', '0104', 58),
            ('W', False, False, True, '0101', '0104', 64),
            ('D', True, True, True, '0101', '0104', 55),
            ('-', False, False, False, '0101', '0104', 76),
            ('D', False, False, False, '0101', '0104', 73),
            ('S', True, False, False, '0101', '0104', 64),
            ('-', True, True, True, '0101', '0104', 58),
            ('N', False, True, False, '0101', '0104', 67),
        ]

        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        sector = Sector('# Core', '# 0, 0')

        for a_base, a_subsec, a_sec, a_other, a_hex, b_hex, expected in cases:
            with self.subTest():
                raw_uwp = 'A555555-8'
                neighbour = Star()
                neighbour.uwp = UWP(raw_uwp)
                neighbour.tradeCode = TradeCodes('')
                neighbour.hex = Hex(sector, b_hex)
                neighbour.importance = 1
                neighbour.baseCode = '-'
                neighbour.zone = '-'
                neighbour.ru = 0

                star = Star()
                star.uwp = UWP(raw_uwp)
                star.hex = Hex(sector, a_hex)
                star.importance = 2
                star.baseCode = a_base
                raw_trade = ''
                if a_subsec:
                    raw_trade += ' Cp'
                if a_sec:
                    raw_trade += ' Cs'
                if a_other:
                    raw_trade += ' Cx'
                star.tradeCode = TradeCodes(raw_trade)

                self.assertEqual(expected, calc.route_weight(star, neighbour))
                self.assertEqual(expected, calc.route_weight(neighbour, star))

    def test_route_weight_3(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        sector = Sector('# Core', '# 0, 0')
        raw_uwp = 'A555555-8'

        neighbour = Star()
        neighbour.sector = sector
        neighbour.name = 'Neighbour'
        neighbour.hex = Hex(sector, '0101')
        neighbour.position = '0101'
        neighbour.uwp = UWP(raw_uwp)
        neighbour.tradeCode = TradeCodes('')
        neighbour.baseCode = '-'
        neighbour.importance = 0
        self.assertEqual('Neighbour (Core 0101)', str(neighbour))

        star = Star()
        star.sector = sector
        star.name = 'Star'
        star.hex = Hex(sector, '0101')
        star.position = '0101'
        star.uwp = UWP(raw_uwp)
        star.tradeCode = TradeCodes('')
        star.baseCode = '-'
        star.importance = 0
        self.assertEqual('Star (Core 0101)', str(star))

        msg = None
        try:
            calc.route_weight(star, neighbour)
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Weight of edge between Star (Core 0101) and Neighbour (Core 0101) must be positive', msg)

    def test_route_weight_4(self) -> None:
        galaxy = Galaxy(8)
        calc = XRouteCalculation(galaxy)
        sector = Sector('# Core', '# 0, 0')
        raw_uwp = 'A555555-8'

        neighbour = Star()
        neighbour.sector = sector
        neighbour.name = 'Neighbour'
        neighbour.hex = Hex(sector, '0101')
        neighbour.position = '0101'
        neighbour.uwp = UWP(raw_uwp)
        neighbour.tradeCode = TradeCodes('')
        neighbour.baseCode = '-'
        neighbour.importance = 0
        self.assertEqual('Neighbour (Core 0101)', str(neighbour))

        star = Star()
        star.sector = sector
        star.name = 'Star'
        star.hex = Hex(sector, '0101')
        star.position = '0101'
        star.uwp = UWP(raw_uwp)
        star.port = 'C'
        star.tradeCode = TradeCodes('Cp Cs Cx')
        star.baseCode = 'W'
        star.importance = 0
        self.assertEqual('Star (Core 0101)', str(star))
        expected = 1

        self.assertEqual(expected, calc.route_weight(star, neighbour))
        self.assertEqual(expected, calc.route_weight(neighbour, star))

    def test_generate_routes_1(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        star = galaxy.stars.nodes[284]['star']
        star.tradeCode = TradeCodes('Cx')

        calc = XRouteCalculation(galaxy)
        logger = calc.logger
        logger.manager.disable = 10
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:generating jumps...',
            'INFO:PyRoute.TradeCalculation:base routes: 5264  -  ranges: 0'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.generate_routes()
            self.assertEqual(exp_logs, logs.output)
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(1, len(calc.secCapitals))
        self.assertEqual(13, len(calc.subCapitals))
        exp_weight = [0, 95, 90, 85, 75, 75, 70]
        self.assertEqual(exp_weight, calc.distance_weight)
        self.assertEqual(0, galaxy.ranges.number_of_edges())
        self.assertEqual(5264, galaxy.stars.number_of_edges())

    def test_calculate_routes_1(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')
        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        star = galaxy.stars.nodes[284]['star']
        star.tradeCode = TradeCodes('Cx')

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:XRoute pass 1',
            'INFO:PyRoute.TradeCalculation:[Unchin (Zarushagar 0522)]',
            'INFO:PyRoute.TradeCalculation:XRoute pass 2',
            'INFO:PyRoute.TradeCalculation:[Liasdi (Zarushagar 0928), Unchin (Zarushagar 0522)]',
            'INFO:PyRoute.TradeCalculation:XRoute pass 3',
            'INFO:PyRoute.TradeCalculation:Important worlds: 10, jump stations: 96',
            'INFO:PyRoute.TradeCalculation:No route for important world: Aashrikan (Zarushagar 1740)',
            'INFO:PyRoute.TradeCalculation:Important worlds: 1, jump stations: 105'
        ]
        calc.generate_routes()
        with self.assertLogs(logger, 'INFO') as logs:
            calc.calculate_routes()
            self.assertEqual(exp_logs, logs.output)

        capital = calc.capital[0]
        secCapital = calc.secCapitals[0]
        edge = galaxy.ranges[capital][secCapital]
        route = edge['route']
        exp_weights = [24, 28]
        for i in range(2):
            start = route[i]
            fin = route[i + 1]
            foo = galaxy.stars[start.index][fin.index]
            self.assertEqual(exp_weights[i], foo['weight'])

        trade_25 = calc.calc_trade(25)
        trade_23 = calc.calc_trade(23)
        trade_21 = calc.calc_trade(21)
        for item in galaxy.stars.edges(data=True):
            trade = item[2]['trade']
            if 0 == trade:
                continue
            self.assertTrue(trade_25 == trade or trade_23 == trade or trade_21 == trade, 'Unexpected trade value: ' + str(trade))

    def test_routes_pass_1_1(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_1/Zarushagar.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_1/Dagudashaag.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        capname = 'Unchin'
        stars = [item['star'] for item in galaxy.stars.nodes.values() if capname == item['star'].name]
        star = stars[0]
        star.tradeCode = TradeCodes('Cx')

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(2, len(calc.secCapitals))
        self.assertEqual(29, len(calc.subCapitals))
        calc.calculate_components()
        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        calc.routes_pass_1()
        exp_weight = [0, 95, 90, 85, 75, 75, 70]
        self.assertEqual(exp_weight, calc.distance_weight)
        self.assertEqual(3, galaxy.ranges.number_of_edges())
        self.assertEqual(2668, galaxy.stars.number_of_edges())
        names = [
            ['Unchin', 'Glomar', 'Liasdi'],
            ['Unchin', 'Siam', 'Iimii', 'Resra', 'Tatsu', 'Mccandliss', 'Kiezupug', 'Lenashuuk', 'Shulasgu', 'Piileir',
             'Vipac', 'Sennirak', 'Medurma'],
            ['Liasdi', 'Vogasphere', 'Ishag', 'Arneua', 'Stonie', 'Seeplis', 'Citenic', 'Hypaethral', 'Khii', 'Aalimru',
             'Sabhaash', 'Piileir', 'Vipac', 'Sennirak', 'Medurma']
        ]
        exp_trade = calc.calc_trade(25)
        distance = [8, 46, 50]
        act_distance = [8, 47, 54]
        exp_trade_count = defaultdict(int)
        for line in names:
            for item in line:
                exp_trade_count[item] += 1
        exp_weight = [
            [44, 44],
            [44, 42, 35, 40, 44, 49, 37, 60, 62, 33, 43, 41],
            [45, 40, 44, 44, 47, 47, 42, 42, 47, 49, 40, 33, 43, 41]
        ]
        exp_count = [
            [1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
        ]

        counter = 0
        for item in galaxy.ranges.edges(data=True):
            self.assertEqual(len(names[counter]), len(item[2]['route']))
            self.assertEqual(distance[counter], item[2]['distance'])
            self.assertEqual(act_distance[counter], item[2]['actual distance'])
            self.assertEqual(len(item[2]['route']) - 1, item[2]['jumps'])
            for i in range(len(names[counter])):
                self.assertEqual(names[counter][i], item[2]['route'][i].name)
                if i < len(names[counter]) - 1:
                    first = item[2]['route'][i]
                    second = item[2]['route'][i + 1]
                    self.assertEqual(exp_trade_count[first.name], first.tradeCount)
                    firstdex = first.index
                    seconddex = second.index
                    edge = galaxy.stars[firstdex][seconddex]
                    self.assertEqual(exp_trade, edge['trade'])
                    self.assertEqual(exp_weight[counter][i], edge['weight'])
                    self.assertEqual(exp_count[counter][i], edge['count'], 'Weight - counter ' + str(counter) + ' i ' + str(i))

            counter += 1

    def test_routes_pass_1_2(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Core.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Delphi.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Fornast.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Massilia.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Old Expanses.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Diaspora.sec'),
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(5, len(calc.secCapitals))
        calc.calculate_components()
        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        galaxy.sectors['Core'].rimward = None
        galaxy.sectors['Fornast'].spinward = None
        galaxy.sectors['Delphi'].coreward = None
        galaxy.sectors['Massilia'].trailing = None

        calc.routes_pass_1()
        self.assertEqual(13, galaxy.ranges.number_of_edges())

    def test_routes_pass_1_3(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Core.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Delphi.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Fornast.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Massilia.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Old Expanses.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_2/Diaspora.sec'),
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                    route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                    mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                    deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(5, len(calc.secCapitals))
        calc.calculate_components()
        calc.secCapitals.reverse()
        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        galaxy.sectors['Core'].trailing = None
        galaxy.sectors['Fornast'].rimward = None
        galaxy.sectors['Delphi'].spinward = None
        galaxy.sectors['Massilia'].coreward = None

        calc.routes_pass_1()
        self.assertEqual(13, galaxy.ranges.number_of_edges())

    def test_routes_pass_1_4(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_4/Core.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_4/Massilia.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_1_4/Delphi.sec'),
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                    route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                    mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                    deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.sectors['Massilia'].spinward = None

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(2, len(calc.secCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        calc.routes_pass_1()
        self.assertEqual(3, galaxy.ranges.number_of_edges())

    def test_routes_pass_2_1(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_1/Core.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(0, len(calc.secCapitals))
        self.assertEqual(15, len(calc.subCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:[Capital (Core 2118)]'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_2()
            self.assertEqual(exp_logs, logs.output)

        exp_weight = [0, 140, 110, 85, 70, 95, 140]
        self.assertEqual(exp_weight, calc.distance_weight)
        self.assertEqual(114, galaxy.ranges.number_of_edges())

        exp_trade = calc.calc_trade(23)

        for item in galaxy.ranges.edges(data=True):
            route = item[2]['route']
            for i in range(len(route) - 1):
                first = route[i]
                second = route[i + 1]
                firstdex = first.index
                seconddex = second.index
                edge = galaxy.stars[firstdex][seconddex]
                self.assertEqual(exp_trade, edge['trade'])

    def test_routes_pass_2_2(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_1/Core.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        capital = [item for item in galaxy.star_mapping.values() if 'Capital' == item.name]
        capital[0].tradeCode = TradeCodes('Cp')

        calc.generate_routes()
        self.assertEqual(0, len(calc.capital))
        self.assertEqual(0, len(calc.secCapitals))
        self.assertEqual(16, len(calc.subCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:[]',
            'INFO:PyRoute.TradeCalculation:Core has subsector capitals but no sector capital'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_2()
            self.assertEqual(exp_logs, logs.output)

        exp_weight = [0, 140, 110, 85, 70, 95, 140]
        self.assertEqual(exp_weight, calc.distance_weight)
        self.assertEqual(114, galaxy.ranges.number_of_edges())

        exp_trade = calc.calc_trade(23)

        for item in galaxy.ranges.edges(data=True):
            route = item[2]['route']
            for i in range(len(route) - 1):
                first = route[i]
                second = route[i + 1]
                firstdex = first.index
                seconddex = second.index
                edge = galaxy.stars[firstdex][seconddex]
                self.assertEqual(exp_trade, edge['trade'])

    def test_routes_pass_2_3(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_1/Core.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        capital = [item for item in galaxy.star_mapping.values() if 'Capital' == item.name]
        capital[0].tradeCode = TradeCodes('')
        subcaps = [item for item in galaxy.star_mapping.values() if 'Cp' in str(item.tradeCode)]
        for item in subcaps:
            item.tradeCode = TradeCodes('')

        calc.generate_routes()
        self.assertEqual(0, len(calc.capital))
        self.assertEqual(0, len(calc.secCapitals))
        self.assertEqual(0, len(calc.subCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:[]',
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_2()
            self.assertEqual(exp_logs, logs.output)

        exp_weight = [0, 140, 110, 85, 70, 95, 140]
        self.assertEqual(exp_weight, calc.distance_weight)
        self.assertEqual(0, galaxy.ranges.number_of_edges())

    def test_routes_pass_2_4(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_4/Dagudashaag.sec'),
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_4/Zarushagar.sec'),
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        subcaps = [item for item in galaxy.star_mapping.values() if 'Cp' in str(item.tradeCode) and 'Dagudashaag' == item.sector.name]
        for item in subcaps:
            item.tradeCode = TradeCodes('')
        subcaps = [item for item in galaxy.star_mapping.values() if 'Cs' in str(item.tradeCode) and 'Zarushagar' == item.sector.name]
        for item in subcaps:
            item.tradeCode = TradeCodes('')

        calc.generate_routes()
        self.assertEqual(0, len(calc.capital))
        self.assertEqual(1, len(calc.secCapitals))
        self.assertEqual(13, len(calc.subCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:[Medurma (Dagudashaag 2124)]',
            'INFO:PyRoute.TradeCalculation:[]',
            'INFO:PyRoute.TradeCalculation:Zarushagar has subsector capitals but no sector capital'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_2()
            self.assertEqual(exp_logs, logs.output)
        self.assertEqual(89, galaxy.ranges.number_of_edges())

        exp_trade = calc.calc_trade(23)

        for item in galaxy.ranges.edges(data=True):
            route = item[2]['route']
            for i in range(len(route) - 1):
                first = route[i]
                second = route[i + 1]
                firstdex = first.index
                seconddex = second.index
                edge = galaxy.stars[firstdex][seconddex]
                self.assertEqual(exp_trade, edge['trade'])

    def test_routes_pass_2_5(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_2_1/Core.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        capital = [item for item in galaxy.star_mapping.values() if 'Capital' == item.name]
        capital[0].tradeCode = TradeCodes('Cp')

        sector = Sector('# Woop Woop', '# -312, 0')
        sector_star = Star()
        sector_star.uwp = UWP(str(capital[0].uwp))
        sector_star.sector = sector
        sector_star.hex = Hex(sector, '1620')
        sector_star.position = '1620'
        sector_star.tradeCode = TradeCodes('Cs')
        sector_star.alg_code = 'Im'
        sector_star.alg_base_code = 'Im'
        sector_star.allegiance_base = 'Im'
        sector_star.index = len(galaxy.star_mapping)
        sector_star.wtn = 6
        sector_star.star_list_object = StarList('')
        galaxy.stars.add_node(sector_star.index, star=sector_star)

        self.assertEqual(9989, sector_star.distance(capital[0]))
        galaxy.star_mapping[sector_star.index] = sector_star
        galaxy.sectors['Woop Woop'] = sector

        calc.generate_routes()
        calc.secCapitals.append(sector_star)
        self.assertEqual(0, len(calc.capital))
        self.assertEqual(1, len(calc.secCapitals))
        self.assertEqual(16, len(calc.subCapitals))
        calc.calculate_components()

        galaxy.ranges.add_edge(calc.subCapitals[0], calc.subCapitals[1])
        galaxy.ranges.add_edge(calc.subCapitals[0], calc.subCapitals[2])
        galaxy.ranges.add_edge(calc.subCapitals[0], calc.subCapitals[3])
        galaxy.ranges.add_edge(calc.subCapitals[0], calc.subCapitals[4])

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        exp_logs = [
            'INFO:PyRoute.TradeCalculation:[]',
            'INFO:PyRoute.TradeCalculation:Core has subsector capitals but no sector capital',
            'INFO:PyRoute.TradeCalculation:[None (Woop Woop 1620)]'
        ]

        with self.assertLogs(logger, 'INFO') as logs, patch.object(calc, 'get_route_between') as mock_object:
            calc.routes_pass_2()
            self.assertEqual(exp_logs, logs.output)
            self.assertEqual(235, mock_object.call_count)

    def test_route_pass_3_1(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_3_1/Core.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.capital))
        self.assertEqual(0, len(calc.secCapitals))
        self.assertEqual(15, len(calc.subCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        capital = calc.capital[0]
        subcap = calc.subCapitals[0]
        galaxy.ranges.add_edge(capital, subcap, route=[])

        exp_logs = [
            'INFO:PyRoute.TradeCalculation:Important worlds: 20, jump stations: 128',
            'INFO:PyRoute.TradeCalculation:Important worlds: 0, jump stations: 148'
        ]
        calc.routes_pass_2()
        self.assertEqual(114, galaxy.ranges.number_of_edges())

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_3()
            self.assertEqual(exp_logs, logs.output)

        self.assertEqual(232, galaxy.ranges.number_of_edges())

        trade_21 = calc.calc_trade(21)
        trade_23 = calc.calc_trade(23)

        for item in galaxy.ranges.edges(data=True):
            route = item[2]['route']
            for i in range(len(route) - 1):
                first = route[i]
                second = route[i + 1]
                firstdex = first.index
                seconddex = second.index
                edge = galaxy.stars[firstdex][seconddex]
                trade = edge['trade']
                self.assertTrue(trade in [trade_21, trade_23], 'Unexpected trade value ' + str(trade)
                                + ' for edge ' + first.name + " " + second.name)

    def test_route_pass_3_2(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_3_2/Zarushagar.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.secCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        calc.routes_pass_2()
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:Important worlds: 1, jump stations: 3',
            'INFO:PyRoute.TradeCalculation:No route for important world: Lenox (Zarushagar 0621)',
            'INFO:PyRoute.TradeCalculation:Important worlds: 1, jump stations: 3'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_3()
            self.assertEqual(exp_logs, logs.output)

        trade_23 = calc.calc_trade(23)
        trade_21 = calc.calc_trade(21)

        for item in galaxy.stars.edges(data=True):
            trade = item[2]['trade']
            self.assertTrue(trade_21 == trade or trade_23 == trade)

    def test_route_pass_3_3(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_3_3/Dagudashaag.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.secCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        calc.routes_pass_2()
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:Important worlds: 1, jump stations: 18',
            'INFO:PyRoute.TradeCalculation:Important worlds: 0, jump stations: 19'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_3()
            self.assertEqual(exp_logs, logs.output)

    def test_route_pass_3_4(self) -> None:
        sourcefile = [
            self.unpack_filename('DeltaFiles/xroute_routes_pass_3_4/Dagudashaag.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = XRouteCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        self.assertEqual(1, len(calc.secCapitals))
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        # Verify importance
        importance = {'Depot (Dagudashaag 3121)': 2, 'Ushra (Dagudashaag 1016)': 3, 'Medurma (Dagudashaag 2124)': 3}

        for item in galaxy.star_mapping:
            star = galaxy.star_mapping[item]
            name = str(star)
            self.assertEqual(importance[name], star.importance, "Unexpected importance value for " + str(star))

        calc.routes_pass_2()
        exp_logs = [
            'INFO:PyRoute.TradeCalculation:Important worlds: 2, jump stations: 0',
            'INFO:PyRoute.TradeCalculation:No route for important world: Ushra (Dagudashaag 1016)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Depot (Dagudashaag 3121)',
            'INFO:PyRoute.TradeCalculation:Important worlds: 2, jump stations: 0'
        ]

        with self.assertLogs(logger, 'INFO') as logs:
            calc.routes_pass_3()
            self.assertEqual(exp_logs, logs.output)

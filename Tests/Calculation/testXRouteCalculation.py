"""
Created on Oct 17, 2025

@author: CyberiaResurrection
"""
from unittest.mock import patch

from ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
from Position.Hex import Hex
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.XRouteCalculation import XRouteCalculation
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.SystemData.UWP import UWP
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
            'INFO:PyRoute.TradeCalculation:Important worlds: 10, jump stations: 100',
            'INFO:PyRoute.TradeCalculation:No route for important world: Strela (Zarushagar 0407)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Lode (Zarushagar 2908)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Ibaru (Zarushagar 0321)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Lenox (Zarushagar 0621)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Irap (Zarushagar 2630)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Romany (Zarushagar 3129)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Aashrikan (Zarushagar 1740)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Riggs (Zarushagar 2731)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Borderline (Zarushagar 3040)',
            'INFO:PyRoute.TradeCalculation:No route for important world: Gaidraa (Zarushagar 3136)'
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
            fin = route[i+1]
            foo = galaxy.stars[start.index][fin.index]
            self.assertEqual(exp_weights[i], foo['weight'])

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

        counter = 0
        for item in galaxy.ranges.edges(data=True):
            self.assertEqual(len(names[counter]), len(item[2]['route']))
            for i in range(len(names[counter])):
                self.assertEqual(names[counter][i], item[2]['route'][i].name)
                if i < len(names[counter]) - 1:
                    first = item[2]['route'][i]
                    second = item[2]['route'][i+1]
                    firstdex = first.index
                    seconddex = second.index
                    edge = galaxy.stars[firstdex][seconddex]
                    self.assertEqual(exp_trade, edge['trade'])

            counter += 1

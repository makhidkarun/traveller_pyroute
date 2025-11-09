"""
Created on Oct 19, 2023

@author: CyberiaResurrection
"""
import copy

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.StatCalculation import StatCalculation, Populations
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from Tests.baseTest import baseTest
from PyRoute.Utilities.NoNoneDefaultDict import NoNoneDefaultDict


class testStatCalcRegression(baseTest):

    def setUp(self) -> None:
        ParseStarInput.deep_space = {}

    def testStatsCalcWithZeroPopulation(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/stat_calc_division_by_zero_population/Dagudashaag-zero.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 2
        args.min_btn = 15

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

        stats = StatCalculation(galaxy)
        stats.calculate_statistics(args.ally_match)
        stats.write_statistics(args.ally_count, args.ally_match, args.json_data)

    def testStatsCalcReftSector(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/reft-allegiance-pax-balance/Reft Sector.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 2
        args.min_btn = 15

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

        stats = StatCalculation(galaxy)
        stats.calculate_statistics(args.ally_match)
        stats.write_statistics(args.ally_count, args.ally_match, args.json_data)

        gal_stats = galaxy.stats
        expected = {'TLmean': 0, 'TLstddev': 0, 'bases': NoNoneDefaultDict(int), 'code_counts': NoNoneDefaultDict(int),
                    'col_be': 6797.200000000001, 'economy': 381621, 'eti_cargo': 0,
                    'eti_pass': 0, 'eti_worlds': 0, 'gg_count': 93, 'im_be': 6196.989999999999, 'maxPop': 0,
                    'maxPort': 'X', 'maxTL': 0, 'milBudget': 0, 'number': 122, 'passengers': 7817295, 'percapita': 4741,
                    'population': 80481, 'populations': NoNoneDefaultDict(Populations), 'port_size': NoNoneDefaultDict(int),
                    'primary_count': NoNoneDefaultDict(int), 'shipyards': 81, 'spa_people': 23705,
                    'star_count': NoNoneDefaultDict(int), 'stars': 172, 'sum_ru': 121636, 'trade': 143514760000,
                    'tradeDton': 3273603, 'tradeDtonExt': 0, 'tradeExt': 0, 'tradeVol': 144540860000, 'worlds': 1272,
                    '__dict__': {}}
        expected['bases']['Military base'] = 18
        expected['bases']['Naval base'] = 23
        expected['bases']['Scout base'] = 9
        expected['code_counts'].update({'(Orpheides)': 1, '(Tapazmal)': 1, 'Ag': 20, 'An': 1, 'As': 3, 'Chir2': 1,
                                        'Chir4': 1, 'ChirW': 1, 'Cp': 2, 'Da': 7, 'De': 11, 'Di(Droyne)': 1,
                                        'Di(Salika)': 1, 'Droy4': 1, 'Droy6': 1, 'Fl': 2, 'Fo': 2, 'Ga': 7, 'He': 8,
                                        'Hi': 13, 'Ic': 6, 'In': 7, 'Lo': 28, 'Mr': 1, 'Na': 11, 'Ni': 63, 'O:0707': 1,
                                        'O:0926': 2, 'O:1323': 1, 'O:1327': 1, 'O:1628': 1, 'O:1822': 1, 'O:2322': 1,
                                        'O:2325': 1, 'O:2738': 2, 'O:2837': 1, 'O:2838': 1, 'O:Gush-0130': 1,
                                        'O:Troj-3215': 1, 'Oc': 2, 'Pa': 10, 'Ph': 6, 'Pi': 9, 'Po': 20, 'Pr': 6,
                                        'Pz': 9, 'Ri': 9, 'RsA': 1, 'RsB': 1, 'Tapa2': 1, 'Tapa3': 1, 'Tapa4': 1,
                                        'Tapa6': 1, 'Tapa8': 1, 'Va': 15, 'Wa': 3})
        expected['port_size'].update({0: 23, 1: 27, 2: 41, 3: 24, 4: 4, 5: 3, 'A': 22, 'B': 61, 'C': 18, 'D': 11,
                                      'E': 8, 'X': 2})
        expected['primary_count'].update({'A': 3, 'F': 23, 'G': 43, 'K': 31, 'M': 22})
        expected['star_count'][1] = 74
        expected['star_count'][2] = 46
        expected['star_count'][3] = 2
        expected['populations']['Chir'] = Populations()
        expected['populations']['Chir'].count = 3
        expected['populations']['Chir'].population = 6
        expected['populations']['Droy'] = Populations()
        expected['populations']['Droy'].count = 3
        expected['populations']['Droy'].population = 2
        expected['populations']['Huma'] = Populations()
        expected['populations']['Huma'].count = 122
        expected['populations']['Huma'].population = 80467
        expected['populations']['Orph'] = Populations()
        expected['populations']['Orph'].count = 1
        expected['populations']['Orph'].population = 1
        expected['populations']['Orph'].homeworlds.append(galaxy.star_mapping[53])
        expected['populations']['Sali'] = Populations()
        expected['populations']['Sali'].count = 1
        expected['populations']['Tapa'] = Populations()
        expected['populations']['Tapa'].count = 6
        expected['populations']['Tapa'].population = 2
        expected['populations']['Tapa'].homeworlds.append(galaxy.star_mapping[116])
        actual = gal_stats.__getstate__()
        act_pops = actual['populations']
        self.assertEqual(expected['populations'], act_pops)
        self.assertEqual(expected, actual)

        remix = copy.deepcopy(actual)
        self.assertEqual(expected, remix, "Deep-copy not equal to original")

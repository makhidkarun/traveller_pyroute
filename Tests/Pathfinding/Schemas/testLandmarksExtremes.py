"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
from collections import defaultdict

from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksQExtremes import LandmarksQExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksRExtremes import LandmarksRExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksSExtremes import LandmarksSExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksWTNExtremes import LandmarksWTNExtremes
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from Tests.baseTest import baseTest


class testLandmarksExtremes(baseTest):

    def setUp(self) -> None:
        ParseStarInput.deep_space = {}

    def test_q_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 60)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        foo = LandmarksQExtremes(galaxy)

        expected = [
                {0: 57}, {0: 0}
            ]
        actual = foo.get_landmarks()
        self.assertEqual(expected, actual)

    def test_r_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 60)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        foo = LandmarksRExtremes(galaxy)

        expected = [
                {0: 0}, {0: 53}
            ]
        actual = foo.get_landmarks()
        self.assertEqual(expected, actual)

    def test_s_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 120)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        foo = LandmarksSExtremes(galaxy)

        expected = [
                {0: 4}, {0: 115}
            ]
        actual = foo.get_landmarks()
        self.assertEqual(expected, actual)

    def test_axial_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 260)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        foo = LandmarksTriaxialExtremes(galaxy)
        self.assertEqual(260, foo.graph_len)
        self.assertIsInstance(foo.distgraph, DistanceGraph)
        self.assertEqual(float('+inf'), foo.floatinf)

        expected = [
            {0: 132}, {0: 257}, {0: 126}, {0: 136}, {0: 142}, {0: 0}, {0: 242}
        ]
        actual, _ = foo.get_landmarks()
        self.assertEqual(expected, actual)

        actual, _ = foo.get_landmarks()
        self.assertEqual(7, len(actual))
        chunk = actual[3]
        self.assertEqual(136, chunk[0])

    def test_component_landmarks_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 260)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected = defaultdict(set)
        expected[0] = {0, 126, 132, 136, 142, 242, 257}

        foo = LandmarksTriaxialExtremes(galaxy)
        _, actual = foo.get_landmarks()
        self.assertEqual(expected, actual)

    def test_landmarks_of_dagudashaag(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Dagudashaag.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile, 260)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        expected_components = defaultdict(set)
        expected_components[0] = {256, 129, 35, 134, 85, 248, 184}
        expected_components[2] = {258, 259}

        expected_landmarks = [{0: 134, 2: 259}, {0: 256, 2: 258}, {0: 129}, {0: 35}, {0: 85}, {0: 248}, {0: 184}]

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, actual = foo.get_landmarks(btn=btn)
        self.assertEqual(expected_components, actual)
        self.assertEqual(expected_landmarks, landmarks)

    def test_landmarks_of_dagudashaag_and_zarushagar(self) -> None:
        source1 = self.unpack_filename('../DeltaFiles/Dagudashaag.sec')
        source2 = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

        delta = DeltaDictionary()
        sector = SectorDictionary.load_traveller_map_file(source1)
        self.assertIsNotNone(sector, "Sector file not loaded from " + source1)
        delta[sector.name] = sector
        sector = SectorDictionary.load_traveller_map_file(source2, 75)
        self.assertIsNotNone(sector, "Sector file not loaded from " + source1)
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 3

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        expected_components = defaultdict(set)
        expected_components[0] = {129, 165, 266, 520, 555, 558, 562, 620}
        expected_landmarks = [{0: 555}, {0: 620}, {0: 129}, {0: 165}, {0: 266}, {0: 520}, {0: 562}, {0: 558}]

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, actual = foo.get_landmarks(btn)
        self.assertEqual(expected_components, actual)
        self.assertEqual(expected_landmarks, landmarks)

    def test_max_slots(self) -> None:
        cases = [
            (501, 10),
            (500, 12),
            (499, 12),
            (251, 12),
            (250, 14),
            (249, 14),
            (126, 14),
            (125, 15),
            (124, 15)
        ]

        for route_reuse, expected in cases:
            args = self._make_args()
            delta = DeltaDictionary()

            galaxy = DeltaGalaxy(args.btn, args.max_jump)
            galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                                route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)

            foo = LandmarksTriaxialExtremes(galaxy)
            self.assertEqual(expected, foo.max_slots)

    def test_landmarks_on_ibara_subsector_single_component(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        self.assertEqual(1, len(galaxy.trade.components), "Unexpected number of components at J-4")

        expected_landmarks = [{0: 34}, {0: 30}, {0: 27}, {0: 35}]
        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertTrue(isinstance(landmarks, list), 'Landmarks result should be a list')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_landmarks_on_ibara_subsector_multiple_components(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 1

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        self.assertEqual(6, len(galaxy.trade.components), "Unexpected number of components at J-1")

        expected_landmarks = [{0: 29, 2: 13, 4: 34}, {0: 26, 2: 4, 4: 36}, {0: 19, 4: 27}, {0: 0}]
        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertEqual(4, len(landmarks), 'Should have one landmark per component')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_landmarks_on_ibara_subsector_multiple_components_btn_supplied(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 1

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        self.assertEqual(6, len(galaxy.trade.components), "Unexpected number of components at J-1")

        expected_landmarks = [{0: 29, 2: 13, 4: 34}, {0: 26, 2: 4, 4: 36}, {0: 19, 4: 27}, {0: 17}]
        landmarks, _ = galaxy.trade.get_landmarks(btn=btn)
        self.assertEqual(4, len(landmarks), 'Should have one landmark per component')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_landmarks_on_ibara_subsector_two_doubleton_components(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        ibaru = sector['Ibaru']
        items = ibaru.items
        nu_lines = [items[1], items[2], items[35], items[36]]
        ibaru.items = nu_lines

        delta = DeltaDictionary()
        delta[sector.name] = sector
        self.assertEqual(4, delta.lines_count)

        args = self._make_args()
        args.max_jump = 3

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()
        self.assertEqual(2, len(galaxy.trade.components), "Unexpected number of components at J-3")

        expected_landmarks = [{0: 1, 1: 2}]
        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_wtn_landmarks_on_ibara_subsector_single_component(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        foo = LandmarksWTNExtremes(galaxy)
        exp_landmarks = [{0: 18}]
        landmarks = foo.get_landmarks()
        self.assertEqual(exp_landmarks, landmarks)

    def test_landmarks_on_ibara_and_bolivar_subsectors_single_component(self) -> None:
        delta = DeltaDictionary()
        sourcefile = [
            self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec'),
            self.unpack_filename('DeltaFiles/Dagudashaag-Bolivar.sec'),
        ]

        for item in sourcefile:
            sector = SectorDictionary.load_traveller_map_file(item)
            delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        self.assertEqual(2, len(galaxy.trade.components), "Unexpected number of components at J-4")

        expected_landmarks = [{0: 34, 1: 41}, {0: 30, 1: 38}, {0: 61}, {0: 39}, {0: 64}]
        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertTrue(isinstance(landmarks, list), 'Landmarks result should be a list')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_landmarks_on_ibara_and_bolivar_subsectors_trimmed(self) -> None:
        delta = DeltaDictionary()
        sourcefile = [
            (self.unpack_filename('DeltaFiles/Dagudashaag-Bolivar.sec'), 15),
            (self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec'), 14),
        ]

        for item, limit in sourcefile:
            sector = SectorDictionary.load_traveller_map_file(item, limit)
            delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, 2)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        self.assertEqual(3, len(galaxy.trade.components), "Unexpected number of components at J-2")
        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        expected_landmarks = [{0: 4, 1: 13, 2: 10}, {0: 1, 1: 14, 2: 28}, {1: 8, 2: 11}, {2: 5}]
        landmarks, _ = galaxy.trade.get_landmarks(btn=btn)
        self.assertTrue(isinstance(landmarks, list), 'Landmarks result should be a list')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

    def test_landmarks_empty_galaxy(self) -> None:
        delta = DeltaDictionary()

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, 2)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        self.assertEqual(0, len(galaxy.trade.components), "Unexpected number of components at J-2")
        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True) if s.component == n.component]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        expected_landmarks = []
        landmarks, _ = galaxy.trade.get_landmarks(btn=btn)
        self.assertTrue(isinstance(landmarks, list), 'Landmarks result should be a list')
        self.assertEqual(expected_landmarks, landmarks, 'Unexpected landmark result')

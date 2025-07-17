"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
from DeltaDebug.DeltaGalaxy import DeltaGalaxy
from DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from Pathfinding.LandmarkSchemes.LandmarksQExtremes import LandmarksQExtremes
from Pathfinding.LandmarkSchemes.LandmarksRExtremes import LandmarksRExtremes
from Pathfinding.LandmarkSchemes.LandmarksSExtremes import LandmarksSExtremes
from Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes
from Tests.baseTest import baseTest


class testLandmarksExtremes(baseTest):

    def test_q_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

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

        foo = LandmarksQExtremes(galaxy)

        expected = [
                {0: 132, 1: 165, 2: 293, 3: 368, 4: 408, 5: 411, 6: 420, 7: 415},
                {0: 0, 1: 165, 2: 293, 3: 368, 4: 408, 5: 409, 6: 414, 7: 415}
            ]
        actual = foo.get_landmarks(index=True)
        self.assertEqual(expected, actual)

    def test_r_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

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

        foo = LandmarksRExtremes(galaxy)

        expected = [
                {0: 0, 1: 165, 2: 293, 3: 368, 4: 408, 5: 411, 6: 414, 7: 415},
                {0: 486, 1: 165, 2: 293, 3: 368, 4: 408, 5: 409, 6: 420, 7: 415}
            ]
        actual = foo.get_landmarks(index=True)
        self.assertEqual(expected, actual)

    def test_s_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

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

        foo = LandmarksSExtremes(galaxy)

        expected = [
                {0: 413, 1: 165, 2: 293, 3: 368, 4: 408, 5: 409, 6: 414, 7: 415},
                {0: 126, 1: 165, 2: 293, 3: 368, 4: 408, 5: 411, 6: 416, 7: 415}
            ]
        actual = foo.get_landmarks(index=True)
        self.assertEqual(expected, actual)

    def test_axial_extremes_of_zarushagar(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar.sec')

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

        foo = LandmarksTriaxialExtremes(galaxy)

        expected = [
            {0: 132, 5: 411, 6: 420},
            {0: 486, 5: 409, 6: 418},
            {0: 126, 6: 416},
            {0: 0},
            {0: 5},
            {0: 428},
            {0: 413},
            {0: 258},
            {0: 268}
        ]
        actual, _ = foo.get_landmarks(index=True)
        self.assertEqual(expected, actual)

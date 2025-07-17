import argparse
import tempfile
import unittest

from DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testTradeCalculationLandmarks(baseTest):
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

        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertTrue(isinstance(landmarks, list), 'Landmarks result should be a list')
        self.assertEqual("Gishin (Zarushagar 0804)", str(landmarks[0][0]), "Unexpected landmark choice")
        self.assertEqual("New Orlando (Zarushagar 0710)", str(landmarks[1][0]), "Unexpected landmark choice")
        self.assertEqual("Nedadzia (Zarushagar 0701)", str(landmarks[2][0]), "Unexpected landmark choice")
        self.assertEqual("Didraga (Zarushagar 0101)", str(landmarks[3][0]), "Unexpected landmark choice")

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

        landmarks, _ = galaxy.trade.get_landmarks()
        self.assertEqual(3, len(landmarks), 'Should have one landmark per component')
        self.assertEqual("Dorevann (Zarushagar 0708)", str(landmarks[0][0]), "Unexpected landmark choice")
        self.assertEqual("Shadishi (Zarushagar 0310)", str(landmarks[0][2]), "Unexpected landmark choice")
        self.assertEqual("Miller's World (Zarushagar 0607)", str(landmarks[1][0]), "Unexpected landmark choice")
        self.assertEqual("Norsec (Zarushagar 0110)", str(landmarks[1][2]), "Unexpected landmark choice")
        self.assertEqual("Engaki (Zarushagar 0502)", str(landmarks[2][0]), "Unexpected landmark choice")

    def _make_args(self) -> argparse.ArgumentParser:
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = None
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = tempfile.gettempdir()
        args.debug_flag = False
        args.mp_threads = 1
        return args


if __name__ == '__main__':
    unittest.main()

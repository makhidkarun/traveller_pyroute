import argparse
import os
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy


class MyTestCase(unittest.TestCase):
    def test_landmarks_on_ibara_subsector_single_component(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        self.assertEqual(1, len(galaxy.trade.components), "Unexpected number of components at J-4")

        landmarks = galaxy.trade.get_landmarks()
        self.assertTrue(isinstance(landmarks, dict), 'Landmarks result should be a dict')
        self.assertEquals(len(galaxy.trade.components), len(landmarks), 'Should have one landmark per component')
        self.assertEquals("Strela (Zarushagar 0407)", str(landmarks[0]), "Unexpected landmark choice")

    def test_landmarks_on_ibara_subsector_multiple_components(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 1

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        self.assertEqual(6, len(galaxy.trade.components), "Unexpected number of components at J-1")

        landmarks = galaxy.trade.get_landmarks()
        self.assertTrue(isinstance(landmarks, dict), 'Landmarks result should be a dict')
        self.assertEquals(len(galaxy.trade.components), len(landmarks), 'Should have one landmark per component')
        self.assertEquals("Strela (Zarushagar 0407)", str(landmarks[0]), "Unexpected landmark choice")
        self.assertEquals("Ymirial (Zarushagar 0106)", str(landmarks[1]), "Unexpected landmark choice")
        self.assertEquals("San Nuska Kilna (Zarushagar 0108)", str(landmarks[2]), "Unexpected landmark choice")
        self.assertEquals("Toulon-Cadiz (Zarushagar 0510)", str(landmarks[3]), "Unexpected landmark choice")
        self.assertEquals("Gishin (Zarushagar 0804)", str(landmarks[4]), "Unexpected landmark choice")
        self.assertEquals("New Orlando (Zarushagar 0710)", str(landmarks[5]), "Unexpected landmark choice")

    def _make_args(self):
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
        return args

if __name__ == '__main__':
    unittest.main()

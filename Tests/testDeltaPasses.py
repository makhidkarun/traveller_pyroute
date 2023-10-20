import argparse
import unittest.main

from PyRoute.DeltaPasses.AllegianceReducer import AllegianceReducer
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaPasses.AuxiliaryLineReduce import AuxiliaryLineReduce
from PyRoute.DeltaPasses.Canonicalisation import Canonicalisation
from PyRoute.DeltaDebug.DeltaReduce import DeltaReduce
from PyRoute.DeltaPasses.FullLineReduce import FullLineReduce
from PyRoute.DeltaPasses.ImportanceLineReduce import ImportanceLineReduce
from PyRoute.DeltaPasses.WidenHoleReducer import WidenHoleReducer
from PyRoute.DeltaStar import DeltaStar
from Tests.Dummy.DeltaDebug.DummyReduce import DummyReduce
from Tests.baseTest import baseTest


class testDeltaPasses(baseTest):
    def test_canonicalisation_of_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = Canonicalisation(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        # verify each line got reduced
        for line in reducer.sectors.lines:
            reduced = DeltaStar.reduce(line)
            self.assertEqual(line, reduced, "Line not canonicalised")

    def test_canonicalisation_resets_hex_block(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-imbalanced-routes.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DummyReduce(delta, args)
        reducer.jam_interesting = True

        reduction_pass = Canonicalisation(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        expected_hex_line = 'Hex  Name                 UWP       Remarks                               {Ix}   (Ex)    [Cx]   N    B  Z PBG W  A    Stellar         Routes                                   \n'
        expected_dash_line = '---- -------------------- --------- ------------------------------------- ------ ------- ------ ---- -- - --- -- ---- --------------- -----------------------------------------\n'

        headers = reducer.sectors['Zarushagar'].headers
        self.assertEqual(expected_hex_line, headers[38])
        self.assertEqual(expected_dash_line, headers[39])

    def test_full_line_reduction_of_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector
        old_count = len(delta.lines)

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = FullLineReduce(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(old_count, new_count, "At least one line not mapped")
        # verify each line got reduced
        for line in reducer.sectors.lines:
            if not line.startswith('2123 Medurma'):
                self.assertEqual(line, DeltaStar.reduce_all(line), "Line not full-line-reduced")

    def test_auxiliary_line_reduction_of_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Passes/Dagudashaag-subsector-full-reduce.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector
        old_count = len(delta.lines)

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = AuxiliaryLineReduce(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(old_count, new_count, "At least one line not mapped")
        # verify each line got reduced
        for line in reducer.sectors.lines:
            self.assertEqual(line, DeltaStar.reduce_auxiliary(line), "Line not auxiliary-line-reduced")

    def test_importance_line_reduction_of_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Passes/Dagudashaag-subsector-full-reduce.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector
        old_count = len(delta.lines)

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = ImportanceLineReduce(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(old_count, new_count, "At least one line not mapped")
        # verify each line got reduced
        for line in reducer.sectors.lines:
            if not line.startswith('2123 Medurma'):
                self.assertEqual(line, DeltaStar.reduce_importance(line), "Line not importance-line-reduced")

    def test_full_and_auxiliary_line_reduction_of_pre_reduced_lines(self):
        sourcefile = self.unpack_filename('DeltaFiles/Passes/Dagudashaag-auxiliary-reduction-two-lines.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        full_pass = FullLineReduce(reducer)
        reduction_pass = AuxiliaryLineReduce(reducer)

        self.assertTrue(full_pass.preflight(), "Input should be reducible")
        full_pass.run()

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        # verify each line got aux-reduced
        for line in reducer.sectors.lines:
            self.assertEqual(line, DeltaStar.reduce_auxiliary(line), "Line not auxiliary-line-reduced")

    def test_widen_hole_reducer_on_start_of_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(0)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(37, new_count, "Unexpected number of lines after widen-hole reduction")

    def test_widen_hole_reducer_near_far_end_of_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(38)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(38, new_count, "Unexpected number of lines after widen-hole reduction")

    def test_widen_hole_reducer_on_end_of_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(-1, reverse=True)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(33, new_count, "Unexpected number of lines after widen-hole-at-end reduction")

    def test_widen_hole_reducer_near_start_of_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(-38, reverse=True)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(39, new_count, "Unexpected number of lines after widen-hole-at-end reduction")

    def test_widen_hole_reducer_reversing_from_positive_location_in_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(21, reverse=True)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(33, new_count, "Unexpected number of lines after widen-hole-reverse-from-positive reduction")

    def test_widen_hole_reducer_forward_from_negative_location_in_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(-20)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(33, new_count, "Unexpected number of lines after widen-hole-reverse-from-positive reduction")

    def test_widen_hole_reducer_near_middle_of_spiked_subsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-subsector-spiked.sec')
        args = self._make_args_no_line()

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = WidenHoleReducer(reducer)
        reduction_pass.run(20)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(37, new_count, "Unexpected number of lines after widen-middle-hole-foward reduction")

        reduction_pass.run(-17, reverse=True)

        reducer.is_initial_state_interesting()
        new_count = len(reducer.sectors.lines)
        self.assertEqual(22, new_count, "Unexpected number of lines after widen-middle-hole-reverse reduction")

    def test_allegiance_reduction_of_sector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Dagudashaag-spiked.sec')
        args = self._make_args_no_line()
        args.interesting_line = 'duplicated'
        args.interesting_type = 'AssertionError'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)
        reducer.is_initial_state_interesting()

        reduction_pass = AllegianceReducer(reducer)

        self.assertTrue(reduction_pass.preflight(), "Input should be reducible")
        reduction_pass.run()

        reducer.is_initial_state_interesting()
        # verify final-state summary
        expected_allegiances = set(["ImDv"])
        actual_allegiances = reducer.sectors.allegiance_list()
        self.assertEqual(expected_allegiances, actual_allegiances, "Unexpected allegiance set after reduction")
        self.assertEqual(508, len(reducer.sectors.lines), "Unexpected number of lines after reduction")
        # verify sector allegiance list got trimmed down
        headers = reducer.sectors['Dagudashaag'].headers
        allegiance_lines = [line for line in headers if "Alleg:" in line]
        self.assertEqual(len(actual_allegiances), len(allegiance_lines), "Allegiance-list length mismatch")
        self.assertTrue("ImDv" in allegiance_lines[0], "Unexpected remaining allegiance")

    def _make_args(self):
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = "Weight of edge"
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = ''
        args.mp_threads = 1
        args.debug_flag = False
        return args

    def _make_args_no_line(self):
        args = self._make_args()
        args.interestingline = None

        return args


if __name__ == '__main__':
    unittest.main()

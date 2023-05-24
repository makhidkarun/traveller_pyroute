import argparse
import unittest
import logging

from PyRoute.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaReduce import DeltaReduce
from PyRoute.route import set_logging


class testDeltaReduce(unittest.TestCase):
    def test_subsector_reduction(self):
        sourcefile = 'DeltaFiles/Dagudashaag-spiked.sec'

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
        args.maps = False
        args.subsectors = False
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)

        reducer.is_initial_state_interesting()
        reducer.reduce_subsector_pass()

        self.assertEqual(1, len(reducer.sectors))
        # only one subsector should be non-empty after reduction
        for subsector_name in reducer.sectors['Dagudashaag']:
            expected = 0
            if subsector_name == 'Pact':
                expected = 40
            actual = 0 if reducer.sectors['Dagudashaag'][subsector_name].items is None else len(reducer.sectors['Dagudashaag'][subsector_name].items)
            self.assertEqual(expected, actual, subsector_name + " not empty")
        # verify sector headers got taken across
        self.assertEqual(len(sector.headers), len(reducer.sectors['Dagudashaag'].headers), "Unexpected headers length")
        # verify sector allegiances got taken across
        self.assertEqual(
            len(sector.allegiances),
            len(reducer.sectors['Dagudashaag'].allegiances),
            "Unexpected allegiances length"
        )

    def test_line_reduction(self):
        sourcefile = 'DeltaFiles/Dagudashaag-subsector-spiked.sec'

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

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        reducer = DeltaReduce(delta, args)

        reducer.is_initial_state_interesting()
        reducer.reduce_line_pass()

        self.assertEqual(1, len(reducer.sectors))
        # only one subsector should be non-empty after reduction
        for subsector_name in reducer.sectors['Dagudashaag']:
            expected = 0
            if subsector_name == 'Pact':
                expected = 4
            self.assertEqual(expected, len(reducer.sectors['Dagudashaag'][subsector_name].items), subsector_name + " not empty")

        # now verify 1-minimality by removing only one line of input at a time
        reducer.reduce_line_pass(singleton_only=True)
        # only one subsector should be non-empty after reduction
        for subsector_name in reducer.sectors['Dagudashaag']:
            expected = 0
            if subsector_name == 'Pact':
                expected = 2
            self.assertEqual(expected, len(reducer.sectors['Dagudashaag'][subsector_name].items), subsector_name + " not empty")

        # verify sector headers got taken across
        self.assertEqual(len(sector.headers), len(reducer.sectors['Dagudashaag'].headers), "Unexpected headers length")
        # verify sector allegiances got taken across
        self.assertEqual(
            len(sector.allegiances),
            len(reducer.sectors['Dagudashaag'].allegiances),
            "Unexpected allegiances length"
        )

    def test_sector_reduction(self):
        sourcefile = 'DeltaFiles/Dagudashaag-spiked.sec'

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

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,0', sector.position, "Unexpected position value for Dagudashaag")
        delta = DeltaDictionary()
        delta[sector.name] = sector

        sourcefile = 'DeltaFiles/Zarushagar.sec'
        zarusector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertEqual('# -1,-1', zarusector.position, "Unexpected position value for Zarushagar")
        delta[zarusector.name] = zarusector

        reducer = DeltaReduce(delta, args)

        reducer.is_initial_state_interesting()
        reducer.reduce_sector_pass()

        self.assertEqual(1, len(reducer.sectors))
        self.assertEqual('Dagudashaag', reducer.sectors['Dagudashaag'].name)

if __name__ == '__main__':
    unittest.main()

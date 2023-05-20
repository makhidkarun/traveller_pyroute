import codecs
import unittest
import sys
from pathlib import Path

from PyRoute.DeltaDictionary import DeltaDictionary, SectorDictionary, SubsectorDictionary

sys.path.append('../PyRoute')


class testDeltaDictionary(unittest.TestCase):
    def test_add_bad_item_by_index(self):
        expected = 'Values must be SectorDictionary objects'
        actual = None

        try:
            foo = DeltaDictionary()
            foo['sector'] = 'bar'

        except AssertionError as e:
            actual = str(e)

        self.assertEqual(expected, actual)

    def test_add_bad_item_by_update(self):
        expected = 'Values must be SectorDictionary objects'
        actual = None

        try:
            foo = DeltaDictionary()
            foo.update({"foo": "bar"})

        except AssertionError as e:
            actual = str(e)

        self.assertEqual(expected, actual)

    def test_add_good_item_by_index(self):
        foo = DeltaDictionary()
        sector = SectorDictionary('name', 'filename')

        foo['sector'] = sector
        self.assertEqual(1, len(foo.keys()), "Target delta dictionary should have one key")

    def test_add_good_item_by_update(self):
        foo = DeltaDictionary()
        sector = SectorDictionary('name', 'filename')

        foo.update({'sector': sector})
        self.assertEqual(1, len(foo.keys()), "Target delta dictionary should have one key")


class testSectorDictionary(unittest.TestCase):
    def test_add_bad_item_by_index(self):
        expected = 'Values must be SubsectorDictionary objects'
        actual = None

        try:
            foo = SectorDictionary('name', 'filename')
            foo['sector'] = 'bar'

        except AssertionError as e:
            actual = str(e)

        self.assertEqual(expected, actual)

    def test_add_bad_item_by_update(self):
        expected = 'Values must be SubsectorDictionary objects'
        actual = None

        try:
            foo = SectorDictionary('name', 'filename')
            foo.update({"foo": "bar"})

        except AssertionError as e:
            actual = str(e)

        self.assertEqual(expected, actual)

    def test_add_good_item_by_index(self):
        foo = SectorDictionary('name', 'filename')
        subsector = SubsectorDictionary('name')
        self.assertEqual(0, len(subsector.keys()), 'Subsector dictionary should be empty')
        self.assertEqual('name', subsector.name)

        foo['sector'] = subsector
        self.assertEqual(1, len(foo.keys()), "Target sector dictionary should have one key")
        self.assertEqual('name', foo.name)
        self.assertEqual('filename', foo.filename)

    def test_add_good_item_by_update(self):
        foo = SectorDictionary('name', 'filename')
        subsector = SubsectorDictionary('name')
        self.assertEqual(0, len(subsector.keys()), 'Subsector dictionary should be empty')
        self.assertEqual('name', subsector.name)

        foo.update({'subsector': subsector})
        self.assertEqual(1, len(foo.keys()), "Target sector dictionary should have one key")
        self.assertEqual('name', foo.name)
        self.assertEqual('filename', foo.filename)

    def test_load_from_traveller_map_file(self):
        sourcefile = 'DeltaFiles/Dagudashaag-spiked.sec'

        # load_traveller_map_file is a little slow as it uses Star's parse_line_into_star method
        # to validate the input line
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertTrue(isinstance(sector, SectorDictionary), "SectorDictionary object not created")

        self.assertEqual('Dagudashaag-spiked.sec', sector.filename)
        self.assertEqual('Dagudashaag', sector.name)
        self.assertEqual('# -1,0', sector.position)
        self.assertTrue(isinstance(sector.headers, list), 'Sector headers not set after load')
        self.assertEqual(41, len(sector.headers), "Unexpected header length after load")
        self.assertEqual(16, len(sector.keys()), "Sector dictionary should have 16 subsector dicts")
        self.assertEqual(561, len(sector.lines), "Unexpected number of star lines after load")

        # now check size of each subsector
        sub_sizes = {'Mimu': 37, 'Old Suns': 32, 'Arnakhish': 37, 'Iiradu': 33, 'Shallows': 40, 'Ushra': 31,
                     'Khandi': 28, 'Kuriishe': 33, 'Zeda': 38, 'Remnants': 38, 'Pact': 40, 'Gadde': 37, 'Bolivar': 29,
                     'Argi': 34, 'Sapphyre': 37, 'Laraa': 37}

        for subname in sub_sizes:
            self.assertEqual(
                sub_sizes[subname],
                len(sector[subname].lines),
                "Unexpected number of star lines in " + subname + " subsector after load"
            )

if __name__ == '__main__':
    unittest.main()

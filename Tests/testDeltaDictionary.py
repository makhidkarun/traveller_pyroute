import unittest
import sys

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

if __name__ == '__main__':
    unittest.main()

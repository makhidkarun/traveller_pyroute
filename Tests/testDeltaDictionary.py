import codecs
import unittest
import sys
from pathlib import Path

from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary, SubsectorDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Galaxy import Allegiance, Galaxy

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

    def test_sector_subset(self):
        foo = DeltaDictionary()
        dag = SectorDictionary('Dagudashaag', 'filename')
        alg = Allegiance('fo', 'foo')
        alg.stats.passengers = 10
        alg.stats.trade = 11
        alg.stats.tradeExt = 42
        gus = SectorDictionary('Gushemege', 'filename')
        gus.position = '# -2,0'
        gus.allegiances[alg.code] = alg
        gusA = SubsectorDictionary('Riften', 'A')
        gusA.items.append('foo')
        self.assertEqual(1, len(gusA.items))
        gusB = SubsectorDictionary('Khiira', 'B')
        gus[gusA.name] = gusA
        gus[gusB.name] = gusB

        foo[dag.name] = dag
        foo[gus.name] = gus

        sectorlist = ['Gushemege']

        remix = foo.sector_subset(sectorlist)
        self.assertTrue(isinstance(remix, DeltaDictionary))
        self.assertEqual(1, len(remix), 'Subsetted delta dict should have one element')
        self.assertEqual('Gushemege', remix['Gushemege'].name)
        self.assertEqual('# -2,0', remix['Gushemege'].position)
        self.assertEqual(2, len(remix['Gushemege']), 'Subsetted delta dict should have two subsectors in single element')
        self.assertEqual(
            1,
            len(remix['Gushemege']['Riften'].items),
            'Riften subsector in subsetted dict should have 1 element'
        )
        # check allegiances got cleared
        self.assertEqual(1, len(remix['Gushemege'].allegiances), "Unexpected allegiance count for Dagudashaag")
        nu_alg = remix['Gushemege'].allegiances['fo']
        self.assertEqual(0, nu_alg.stats.passengers, "Allegiance pax not cleared during sector_list")
        self.assertEqual(0, nu_alg.stats.trade, "Allegiance trade not cleared during sector_list")
        self.assertEqual(0, nu_alg.stats.tradeExt, "Allegiance tradeExt not cleared during sector_list")

    def test_subsector_subset(self):
        foo = DeltaDictionary()
        dag = SectorDictionary('Dagudashaag', 'filename')
        alg = Allegiance('fo', 'foo')
        alg.stats.passengers = 10
        alg.stats.trade = 11
        alg.stats.tradeExt = 42
        dag.allegiances[alg.code] = alg
        dagA = SubsectorDictionary('Mimu', 'A')
        dag[dagA.name] = dagA
        dag.position = '# -1,0'
        gus = SectorDictionary('Gushemege', 'filename')
        gusA = SubsectorDictionary('Riften', 'A')
        gusA.items.append('foo')
        self.assertEqual(1, len(gusA.items))
        gusB = SubsectorDictionary('Khiira', 'B')
        gusB.items.append('bar')
        gus[gusA.name] = gusA
        gus[gusB.name] = gusB
        gus.position = '# -2,0'

        foo[dag.name] = dag
        foo[gus.name] = gus

        subsectorlist = ['Mimu', 'Khiira']

        remix = foo.subsector_subset(subsectorlist)
        self.assertTrue(isinstance(remix, DeltaDictionary))
        self.assertEqual(2, len(remix), 'Subsetted delta dict should have two element')
        self.assertEqual('Gushemege', remix['Gushemege'].name)
        self.assertEqual('# -2,0', remix['Gushemege'].position)
        self.assertEqual('filename', remix['Gushemege'].filename)
        self.assertEqual(2, len(remix['Gushemege']),
                         'Subsetted delta dict should two one subsector in Gushemege')
        self.assertEqual('Khiira', remix['Gushemege']['Khiira'].name)
        self.assertEqual('Riften', remix['Gushemege']['Riften'].name)
        self.assertEqual(None, remix['Gushemege']['Riften'].items, 'Skipped subsector should have None for items')
        self.assertEqual('Dagudashaag', remix['Dagudashaag'].name)
        self.assertEqual('# -1,0', remix['Dagudashaag'].position)
        self.assertEqual(1, len(remix['Dagudashaag']),
                         'Subsetted delta dict should have one subsector in Dagudashaag')
        self.assertEqual('Mimu', remix['Dagudashaag']['Mimu'].name)
        self.assertEqual('A', remix['Dagudashaag']['Mimu'].position)
        # check allegiances got cleared
        self.assertEqual(1, len(remix['Dagudashaag'].allegiances), "Unexpected allegiance count for Dagudashaag")
        nu_alg = remix['Dagudashaag'].allegiances['fo']
        self.assertEqual(0, nu_alg.stats.passengers, "Allegiance pax not cleared during subsector_list")
        self.assertEqual(0, nu_alg.stats.trade, "Allegiance trade not cleared during subsector_list")
        self.assertEqual(0, nu_alg.stats.tradeExt, "Allegiance tradeExt not cleared during subsector_list")

    def test_sector_list(self):
        foo = DeltaDictionary()
        dag = SectorDictionary('Dagudashaag', 'filename')
        dagA = SubsectorDictionary('Mimu', 'A')
        dag[dagA.name] = dagA
        gus = SectorDictionary('Gushemege', 'filename')
        gusA = SubsectorDictionary('Riften', 'A')
        gusA.items.append('foo')
        self.assertEqual(1, len(gusA.items))
        gusB = SubsectorDictionary('Khiira', 'B')
        gus[gusA.name] = gusA
        gus[gusB.name] = gusB

        foo[dag.name] = dag
        foo[gus.name] = gus

        expected = list()
        expected.append('Gushemege')
        expected.append('Dagudashaag')
        expected.sort()
        actual = foo.sector_list()

        self.assertEqual(expected, actual, "Unexpected sector list")

    def test_subsector_list(self):
        foo = DeltaDictionary()
        dag = SectorDictionary('Dagudashaag', 'filename')
        dagA = SubsectorDictionary('Mimu', 'A')
        dag[dagA.name] = dagA
        gus = SectorDictionary('Gushemege', 'filename')
        gusA = SubsectorDictionary('Riften', 'A')
        gusA.items.append('foo')
        self.assertEqual(1, len(gusA.items))
        gusB = SubsectorDictionary('Khiira', 'B')
        gus[gusA.name] = gusA
        gus[gusB.name] = gusB

        foo[dag.name] = dag
        foo[gus.name] = gus

        expected = list()
        expected.append('Khiira')
        expected.append('Mimu')
        expected.append('Riften')
        actual = foo.subsector_list()

        self.assertEqual(expected, actual, "Unexpected subsector list")

        gusB.items = None

        expected = list()
        expected.append('Mimu')
        expected.append('Riften')
        actual = foo.subsector_list()

        self.assertEqual(expected, actual, "Unexpected subsector list")

    def test_sector_subset_blowup_on_vland_empty(self):
        vland = 'DeltaFiles/sector_subset_blowup_on_vland_empty/Vland.sec'

        vland_sec = SectorDictionary.load_traveller_map_file(vland)

        foo = DeltaDictionary()
        foo[vland_sec.name] = vland_sec

        remix = foo.sector_subset(['Vland'])
        self.assertEqual(1, len(remix))

    def test_sector_subset_blowup_on_spinward_marches(self):
        spinward = 'DeltaFiles/high_pop_worlds_blowup/Spinward Marches.sec'

        spinward_sec = SectorDictionary.load_traveller_map_file(spinward)

        del spinward_sec.allegiances['CsIm'].stats.high_pop_worlds

        foo = DeltaDictionary()
        foo[spinward_sec.name] = spinward_sec

        remix = foo.sector_subset(['Spinward Marches', 'Deneb', 'Trojan Reach'])
        self.assertEqual(1, len(remix))
        self.assertListEqual([], remix['Spinward Marches'].allegiances['CsIm'].stats.high_pop_worlds, "Missing high_pop_worlds list not restored")

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
        subsector = SubsectorDictionary('name', 'A')
        self.assertEqual(0, len(subsector.keys()), 'Subsector dictionary should be empty')
        self.assertEqual('name', subsector.name)

        foo['sector'] = subsector
        self.assertEqual(1, len(foo.keys()), "Target sector dictionary should have one key")
        self.assertEqual('name', foo.name)
        self.assertEqual('filename', foo.filename)

    def test_add_good_item_by_update(self):
        foo = SectorDictionary('name', 'filename')
        subsector = SubsectorDictionary('name', 'A')
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
        sub_positions = {'Mimu': 'A', 'Old Suns': 'B', 'Arnakhish': 'C', 'Iiradu': 'D', 'Shallows': 'E', 'Ushra': 'F',
                     'Khandi': 'G', 'Kuriishe': 'H', 'Zeda': 'I', 'Remnants': 'J', 'Pact': 'K', 'Gadde': 'L',
                     'Bolivar': 'M', 'Argi': 'N', 'Sapphyre': 'O', 'Laraa': 'P'}

        for subname in sub_sizes:
            self.assertEqual(
                sub_sizes[subname],
                len(sector[subname].lines),
                "Unexpected number of star lines in " + subname + " subsector after load"
            )
            self.assertEqual(
                sub_positions[subname],
                sector[subname].position,
                'Unexpected position for ' + subname + ' subsector after load'
            )

        # verify allegiances got read in and derived allegiances calculated
        self.assertEqual(4, len(sector.allegiances), "Unexpected number of allegiances after load")

    def test_drop_lines(self):
        alg = Allegiance('fo', 'foo')
        alg.stats.passengers = 10
        alg.stats.trade = 11
        alg.stats.tradeExt = 42

        foo = SectorDictionary('name', 'filename')
        foo.allegiances[alg.code] = alg

        sub1 = SubsectorDictionary('Mimu', 'A')
        sub1.items.append('foo')
        sub1.items.append('bar')
        sub2 = SubsectorDictionary('Khiira', 'B')
        sub2.items.append('baz')
        sub2.items.append('tree')
        sub3 = SubsectorDictionary('Old Suns', 'C')
        sub3.items = None
        self.assertTrue(sub3.skipped)

        foo[sub1.name] = sub1
        foo[sub2.name] = sub2
        foo[sub3.name] = sub3

        expected = list()
        expected.append('foo')
        expected.append('bar')
        expected.append('baz')
        expected.append('tree')
        actual = foo.lines
        self.assertEqual(expected, actual)

        lines_to_drop = ['bar', 'tree']
        remix = foo.drop_lines(lines_to_drop)

        actual = foo.lines
        self.assertEqual(expected, actual)
        expected = list()
        expected.append('foo')
        expected.append('baz')
        actual = remix.lines
        self.assertEqual(expected, actual, 'Unexpected lines in new dictionary after line removal')
        self.assertEqual(1, len(remix.allegiances))
        nu_alg = remix.allegiances['fo']
        self.assertEqual(0, nu_alg.stats.passengers, "Allegiance pax not cleared during drop_lines")
        self.assertEqual(0, nu_alg.stats.trade, "Allegiance trade not cleared during drop_lines")
        self.assertEqual(0, nu_alg.stats.tradeExt, "Allegiance tradeExt not cleared during drop_lines")

    def test_empty_sector_dictionary_is_skipped(self):
        foo = SectorDictionary('name', 'filename')
        self.assertEqual(0, len(foo))
        self.assertEqual(0, len(foo.lines))

        self.assertTrue(foo.skipped)

    def test_sector_dictionary_with_one_unskipped_subsector_is_not_skipped(self):
        foo = SectorDictionary('name', 'filename')
        sub1 = SubsectorDictionary('Mimu', 'A')
        foo[sub1.name] = sub1

        self.assertFalse(sub1.skipped)
        self.assertEqual(1, len(foo))
        self.assertEqual(0, len(foo.lines))

        self.assertFalse(foo.skipped)

    def test_sector_dictionary_with_one_skipped_subsector_is_skipped(self):
        foo = SectorDictionary('name', 'filename')
        sub1 = SubsectorDictionary('Mimu', 'A')
        sub1.items = None
        foo[sub1.name] = sub1

        self.assertTrue(sub1.skipped)
        self.assertEqual(1, len(foo))
        self.assertEqual(0, len(foo.lines))

        self.assertTrue(foo.skipped)

class testSubsectorDictionary(unittest.TestCase):
    def test_drop_lines(self):
        foo = SubsectorDictionary('Mimu', 'A')
        foo.items.append('foo')
        foo.items.append('bar')
        foo.items.append('baz')
        self.assertEqual(3, len(foo.items))

        lines_to_drop = ['bar']

        remix = foo.drop_lines(lines_to_drop)
        self.assertEqual(3, len(foo.items))
        self.assertEqual(2, len(remix.items))
        self.assertEqual('Mimu', remix.name)
        self.assertEqual('A', remix.position)

    def test_drop_all_lines_skips_subsector(self):
        foo = SubsectorDictionary('Mimu', 'A')
        foo.items.append('foo')
        foo.items.append('bar')
        foo.items.append('baz')
        self.assertEqual(3, len(foo.items))
        self.assertFalse(foo.skipped)

        lines_to_drop = ['foo', 'bar', 'baz']
        remix = foo.drop_lines(lines_to_drop)
        self.assertTrue(remix.skipped)


if __name__ == '__main__':
    unittest.main()

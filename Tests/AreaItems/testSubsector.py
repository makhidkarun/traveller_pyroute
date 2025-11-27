"""
Created on Nov 27, 2025

@author: CyberiaResurrection
"""

from PyRoute.AreaItems.Sector import Sector
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.StatCalculation import ObjectStatistics
from Tests.baseTest import baseTest


class testSubsector(baseTest):

    def setUp(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        self.sector = Sector(name, position)
        self.spinsec = Sector('# Uptown Woop Woop', '# -6, 4')
        self.coresec = Sector('# Downtown Woop Woop', '# -5, 5')

    def test_get_state(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        exp_dict = {
            '_wiki_name': '[[Foobar Subsector|Foobar]]',
            'alg': {},
            'debug_flag': False,
            'dx': -160,
            'dy': 160,
            'name': 'Foobar',
            'position': 'K',
            'stats': ObjectStatistics(),
            'worlds': []
        }
        self.assertEqual(exp_dict, subsec.__getstate__())

    def test_subsector_name_1(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertEqual("Foobar", subsec.subsector_name())

    def test_subsector_name_2(self) -> None:
        subsec = Subsector("", 'K', self.sector)
        self.assertEqual("Location K", subsec.subsector_name())

    def test_subsector_name_3(self) -> None:
        subsec = Subsector("Foobar Subsector", 'K', self.sector)
        self.assertEqual("Foobar", subsec.subsector_name())

    def test_subsector_name_4(self) -> None:
        subsec = Subsector("FoobarSubsector", 'K', self.sector)
        self.assertEqual("Foobar", subsec.subsector_name())

    def test_wiki_title(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertEqual("[[Foobar Subsector|Foobar]] - [[Fnordia Sector|Fnordia]]", subsec.wiki_title())

    def test_wiki_name_1(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertEqual('[[Foobar Subsector|Foobar]]', subsec.wiki_name())

    def test_wiki_name_2(self) -> None:
        subsec = Subsector("", 'K', self.sector)
        self.assertEqual('Fnordia location K', subsec.wiki_name())

    def test_set_bounding_subsectors_1(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertIsNone(subsec.coreward)
        self.assertIsNone(subsec.rimward)
        self.assertIsNone(subsec.spinward)
        self.assertIsNone(subsec.trailing)
        coreward = Subsector("Rhubarb", 'G', self.sector)
        self.sector.subsectors['G'] = coreward
        spinward = Subsector("Rabble", 'J', self.sector)
        self.sector.subsectors['J'] = spinward
        rimward = Subsector("Woop Woop", 'O', self.sector)
        self.sector.subsectors['O'] = rimward
        trailing = Subsector("Uptown", 'L', self.sector)
        self.sector.subsectors['L'] = trailing

        subsec.set_bounding_subsectors()
        self.assertEqual(coreward.name, subsec.coreward.name)
        self.assertEqual(rimward.name, subsec.rimward.name)
        self.assertEqual(spinward.name, subsec.spinward.name)
        self.assertEqual(trailing.name, subsec.trailing.name)

    def test_set_bounding_subsectors_2(self) -> None:
        self.sector.spinward = self.spinsec
        self.spinsec.trailing = self.sector

        trail_subsec = Subsector("Foobar", 'E', self.sector)
        spin_subsec = Subsector("Barfoo", 'H', self.spinsec)
        self.sector.subsectors['E'] = trail_subsec
        self.sector.subsectors['A'] = Subsector('A', 'A', self.sector)
        self.sector.subsectors['F'] = Subsector('F', 'F', self.sector)
        self.sector.subsectors['I'] = Subsector('I', 'I', self.sector)
        self.spinsec.subsectors['H'] = spin_subsec
        self.spinsec.subsectors['D'] = Subsector('D', 'D', self.spinsec)
        self.spinsec.subsectors['G'] = Subsector('G', 'G', self.spinsec)
        self.spinsec.subsectors['L'] = Subsector('L', 'L', self.spinsec)

        trail_subsec.set_bounding_subsectors()
        spin_subsec.set_bounding_subsectors()
        self.assertEqual(spin_subsec, trail_subsec.spinward)
        self.assertEqual(trail_subsec, spin_subsec.trailing)

    def test_set_bounding_subsectors_3(self) -> None:
        self.sector.coreward = self.coresec
        self.coresec.rimward = self.sector

        rim_subsec = Subsector("Foobar", 'B', self.sector)
        core_subsec = Subsector("Barfoo", 'N', self.coresec)
        self.sector.subsectors['B'] = rim_subsec
        self.sector.subsectors['A'] = Subsector('A', 'A', self.sector)
        self.sector.subsectors['C'] = Subsector('C', 'C', self.sector)
        self.sector.subsectors['F'] = Subsector('F', 'F', self.sector)
        self.coresec.subsectors['N'] = core_subsec
        self.coresec.subsectors['J'] = Subsector('J', 'J', self.coresec)
        self.coresec.subsectors['M'] = Subsector('M', 'M', self.coresec)
        self.coresec.subsectors['O'] = Subsector('O', 'O', self.coresec)

        rim_subsec.set_bounding_subsectors()
        core_subsec.set_bounding_subsectors()

        self.assertEqual(core_subsec, rim_subsec.coreward)
        self.assertEqual(rim_subsec, core_subsec.rimward)

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

    def test_subsector_name(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertEqual("Foobar", subsec.subsector_name())

    def test_wiki_title(self) -> None:
        subsec = Subsector("Foobar", 'K', self.sector)
        self.assertEqual("[[Foobar Subsector|Foobar]] - [[Fnordia Sector|Fnordia]]", subsec.wiki_title())

    def test_set_bounding_subsectors(self) -> None:
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

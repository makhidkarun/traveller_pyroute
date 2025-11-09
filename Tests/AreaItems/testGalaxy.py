"""
Created on Nov 30, 2021

@author: CyberiaResurrection
"""

import unittest

from PyRoute import Star
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.Calculation.NoneCalculation import NoneCalculation
from PyRoute.StatCalculation import ObjectStatistics
from PyRoute.Pathfinding.RouteLandmarkGraph import RouteLandmarkGraph


class testGalaxy(unittest.TestCase):

    def test_get_state(self) -> None:
        galaxy = Galaxy(0)
        exp_dict = {
            '_wiki_name': '[[Charted Space]]',
            'alg': {},
            'big_component': None,
            'debug_flag': False,
            'historic_costs': None,
            'max_jump_range': 4,
            'min_btn': 0,
            'name': 'Charted Space',
            'output_path': 'maps',
            'star_mapping': {},
            'stats': ObjectStatistics(),
            'worlds': []
        }
        self.assertEqual(exp_dict, galaxy.__getstate__())

    def test_is_well_formed(self) -> None:
        galaxy = Galaxy(0)
        galaxy.is_well_formed()

    """
    A very simple, barebones test to check that Verge and Reft end up in their correct relative positions
    - Verge being immediately rimward of Reft
    """
    def testVerticalOrdering(self) -> None:
        galaxy = Galaxy(0)

        reft = Sector("# Reft", "# -3, 0")
        self.assertEqual(-3, reft.x)
        self.assertEqual(0, reft.y)

        verge = Sector("# Verge", "# -3, -1")
        self.assertEqual(-3, verge.x)
        self.assertEqual(-1, verge.y)

        galaxy.sectors[reft.name] = reft
        galaxy.sectors[verge.name] = verge

        # verify, before bounding sectors gets run, nothing is hooked up
        self.assertIsNone(galaxy.sectors[reft.name].coreward)
        self.assertIsNone(galaxy.sectors[reft.name].rimward)
        self.assertIsNone(galaxy.sectors[reft.name].spinward)
        self.assertIsNone(galaxy.sectors[reft.name].trailing)
        self.assertIsNone(galaxy.sectors[verge.name].coreward)
        self.assertIsNone(galaxy.sectors[verge.name].rimward)
        self.assertIsNone(galaxy.sectors[verge.name].spinward)
        self.assertIsNone(galaxy.sectors[verge.name].trailing)

        # set bounding sectors
        galaxy.set_bounding_sectors()

        # now assert that Reft is coreward from Verge, and (likewise), Verge is rimward from Reft, and nothing else
        # got set
        self.assertEqual(galaxy.sectors[reft.name], galaxy.sectors[verge.name].coreward, "Reft should be coreward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].rimward, "Nothing should be rimward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].spinward, "Nothing should be spinward of Verge")
        self.assertIsNone(galaxy.sectors[verge.name].trailing, "Nothing should be trailing of Verge")
        self.assertIsNone(galaxy.sectors[reft.name].coreward, "Nothing should be coreward of Reft")
        self.assertIsNone(galaxy.sectors[reft.name].trailing, "Nothing should be trailing of Reft")
        self.assertIsNone(galaxy.sectors[reft.name].spinward, "Nothing should be spinward of Reft")
        self.assertEqual(galaxy.sectors[verge.name], galaxy.sectors[reft.name].rimward, "Verge should be rimward of Reft")

    """
    A very simple, barebones test to check that Dagudashaag and Core end up in their correct relative positions
    - Dagudashaag being immediately spinward of Core
    """
    def testHorizontalOrdering(self) -> None:
        galaxy = Galaxy(0)

        core = Sector("# Core", "# 0, 0")
        self.assertEqual(0, core.x)
        self.assertEqual(0, core.y)

        dagudashaag = Sector("# Dagudashaag", "# -1, 0")
        self.assertEqual(-1, dagudashaag.x)
        self.assertEqual(0, dagudashaag.y)

        galaxy.sectors[core.name] = core
        galaxy.sectors[dagudashaag.name] = dagudashaag

        # verify, before bounding sectors gets run, nothing is hooked up
        self.assertIsNone(galaxy.sectors[core.name].coreward)
        self.assertIsNone(galaxy.sectors[core.name].rimward)
        self.assertIsNone(galaxy.sectors[core.name].spinward)
        self.assertIsNone(galaxy.sectors[core.name].trailing)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].coreward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].rimward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].spinward)
        self.assertIsNone(galaxy.sectors[dagudashaag.name].trailing)

        # set bounding sectors
        galaxy.set_bounding_sectors()

        # now assert that Dagudashaag is spinward from Core, Core is trailing of Dagudashaag, and nothing else
        # got set
        self.assertEqual(galaxy.sectors[dagudashaag.name], galaxy.sectors[core.name].spinward, "Dagudashaag should be spinward of core")
        self.assertIsNone(galaxy.sectors[core.name].coreward, "Nothing should be coreward of Core")
        self.assertIsNone(galaxy.sectors[core.name].rimward, "Nothing should be rimward of Core")
        self.assertIsNone(galaxy.sectors[core.name].trailing, "Nothing should be trailing of core")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].coreward, "Nothing should be coreward of Dagudashaag")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].rimward, "Nothing should be rimward of Dagudashaag")
        self.assertIsNone(galaxy.sectors[dagudashaag.name].spinward, "Nothing should be spinward of Dagudashaag")
        self.assertEqual(galaxy.sectors[core.name], galaxy.sectors[dagudashaag.name].trailing, "Core should be trailing of Dagudashaag")

    def test_add_star_to_galaxy(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        subs = Subsector('Foobar', 'A', sector)
        sector.subsectors['A'] = subs
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(0)
        galaxy.trade = NoneCalculation(galaxy)
        galaxy.sectors['Core'] = sector
        final = galaxy.add_star_to_galaxy(star1, 1, sector)
        self.assertEqual(2, final)
        galaxy.set_positions()
        self.assertIsInstance(galaxy.historic_costs, RouteLandmarkGraph)

    def test_process_eti(self) -> None:
        sector = Sector('# Core', '# 0, 0')
        subs = Subsector('Foobar', 'A', sector)
        sector.subsectors['A'] = subs
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star2 = Star.parse_line_into_star(
            "0104 Shana Ma             E551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Im K2 IV M7 V     ",
            sector, 'fixed', 'fixed')

        galaxy = Galaxy(0)
        galaxy.trade = NoneCalculation(galaxy)
        galaxy.sectors['Core'] = sector
        galaxy.add_star_to_galaxy(star1, 1, sector)
        galaxy.add_star_to_galaxy(star2, 2, sector)
        galaxy.stars.add_edge(1, 2, btn=0)
        galaxy.process_eti()
        edge = galaxy.stars.get_edge_data(1, 2)
        self.assertEqual(0, edge['CargoTradeIndex'])
        self.assertEqual(0, edge['PassTradeIndex'])

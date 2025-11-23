"""
Created on Nov 24, 2025

@author: CyberiaResurrection
"""

from PyRoute.AreaItems.Sector import Sector
from PyRoute.StatCalculation import ObjectStatistics
from Tests.baseTest import baseTest


class testSector(baseTest):

    def test_non_string_name_bad_pos(self) -> None:
        name = None
        position = ""

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Name must be a string", msg)

    def test_bad_name_non_string_pos(self) -> None:
        name = ""
        position = None

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Position must be a string", msg)

    def test_bad_name_bad_pos(self) -> None:
        name = ""
        position = ""

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Name string too short", msg)

    def test_wonky_name_bad_pos(self) -> None:
        name = "Fnordia"
        position = ""

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Position string too short", msg)

    def test_wonky_name_wonky_pos(self) -> None:
        name = "Fnordia"
        position = " 1, 1"

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Name string should start with #", msg)

    def test_good_name_wonky_pos(self) -> None:
        name = "# Fnordia"
        position = " 1, 1"

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Position string should start with #", msg)

    def test_good_name_malformed_pos(self) -> None:
        name = "# Fnordia"
        position = "# 1  1"

        msg = ""
        try:
            Sector(name, position)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Position string malformed", msg)

    def test_sector_name(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_name = "Fnordia"
        self.assertEqual(exp_name, sector.sector_name())

    def test_str(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_name = "Fnordia (-5,4)"
        self.assertEqual(exp_name, str(sector))

    def test_getstate(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_dict = {
            '_wiki_name': '[[Fnordia Sector|Fnordia]]',
            'alg': {},
            'debug_flag': False,
            'dx': -160,
            'dy': 160,
            'filename': None,
            'name': 'Fnordia',
            'stats': ObjectStatistics(),
            'subsectors': {},
            'worlds': [],
            'x': -5,
            'y': 4
        }
        self.assertEqual(exp_dict, sector.__getstate__())

    def test_is_well_formed(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        well_formed, msg = sector.is_well_formed()
        self.assertTrue(well_formed)
        self.assertEqual("", msg)

    def test_find_world_by_pos(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        self.assertIsNone(sector.find_world_by_pos('0101'))

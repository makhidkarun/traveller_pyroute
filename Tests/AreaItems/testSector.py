"""
Created on Nov 24, 2025

@author: CyberiaResurrection
"""

from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Sector import Sector
from PyRoute.StatCalculation import ObjectStatistics
from PyRoute.AreaItems.Subsector import Subsector
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

    def test_good_short_name_good_short_pos(self) -> None:
        name = "# F"
        position = "# 1,2"
        sector = Sector(name, position)
        self.assertEqual('F', sector.name)
        self.assertEqual(1, sector.x)
        self.assertEqual(2, sector.y)

    def test_good_short_name_good_non_short_pos(self) -> None:
        name = "# F"
        position = "# 1, 2"
        sector = Sector(name, position)
        self.assertEqual('F', sector.name)
        self.assertEqual(1, sector.x)
        self.assertEqual(2, sector.y)

    def test_good_short_name_2_good_short_pos(self) -> None:
        name = "#Fa"
        position = "#1,-2"
        sector = Sector(name, position)
        self.assertEqual('Fa', sector.name)
        self.assertEqual(1, sector.x)
        self.assertEqual(-2, sector.y)

    def test_sector_name(self) -> None:
        name = "  # Fnordia  "
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_name = "Fnordia"
        self.assertEqual(exp_name, sector.sector_name())

    def test_sector_name_with_sector(self) -> None:
        name = "  # Fnordia  Sector"
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_name = "Fnordia"
        self.assertEqual(exp_name, sector.sector_name())

    def test_sector_name_with_sector_2(self) -> None:
        name = "  # FnordiaSector"
        position = "# -5, 4"

        sector = Sector(name, position)
        exp_name = "Fnordia"
        self.assertEqual(exp_name, sector.sector_name())

    def test_sector_name_with_sector_3(self) -> None:
        name = "  # FnordiaSector Sector"
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
        self.assertIsNotNone(msg)
        self.assertEqual("", msg)

    def test_is_well_formed_bad_name(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        sector.name = '  '
        well_formed, msg = sector.is_well_formed()
        self.assertFalse(well_formed)
        self.assertEqual("Name cannot be empty", msg)

    def test_is_well_formed_none_name(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        sector.name = None
        well_formed, msg = sector.is_well_formed()
        self.assertFalse(well_formed)
        self.assertEqual("Name cannot be empty", msg)

    def test_is_well_formed_reciprocity_none(self) -> None:
        cases = [
            ('coreward', "Coreward sector mismatch for Fnordia"),
            ('rimward', "Rimward sector mismatch for Fnordia"),
            ('spinward', "Spinward sector mismatch for Fnordia"),
            ('trailing', "Trailing sector mismatch for Fnordia"),
        ]

        for direction, exp_msg in cases:
            with self.subTest(direction):
                name = "# Fnordia"
                position = "# -5, 4"

                sector = Sector(name, position)

                name = "# Rhubarb"
                position = "# -6, 6"
                rhubarb = Sector(name, position)

                sector.__setattr__(direction, rhubarb)
                well_formed, msg = sector.is_well_formed()
                self.assertFalse(well_formed)
                self.assertEqual(exp_msg, msg)

    def test_is_well_formed_reciprocity_not_self(self) -> None:
        cases = [
            ('coreward', 'rimward', "Coreward sector mismatch for Fnordia"),
            ('rimward', 'coreward', "Rimward sector mismatch for Fnordia"),
            ('spinward', 'trailing', "Spinward sector mismatch for Fnordia"),
            ('trailing', 'spinward', "Trailing sector mismatch for Fnordia"),
        ]

        for direction, reverse, exp_msg in cases:
            with self.subTest(direction):
                name = "# Fnordia"
                position = "# -5, 4"

                sector = Sector(name, position)

                name = "# Rhubarb"
                position = "# -6, 6"
                rhubarb = Sector(name, position)

                sector.__setattr__(direction, rhubarb)
                rhubarb.__setattr__(reverse, rhubarb)
                well_formed, msg = sector.is_well_formed()
                self.assertFalse(well_formed)
                self.assertEqual(exp_msg, msg)

    def test_is_well_formed_reciprocity_co_ord_mismatch(self) -> None:
        cases = [
            ('coreward', 'rimward', "# -6, 4", 'x', "Coreward sector x co-ord mismatch for Fnordia"),
            ('rimward', 'coreward', "# -4, 4", 'x', "Rimward sector x co-ord mismatch for Fnordia"),
            ('spinward', 'trailing', "# -5, 4", 'x', "Spinward sector x co-ord mismatch for Fnordia"),
            ('trailing', 'spinward', "# -5, 4", 'x', "Trailing sector x co-ord mismatch for Fnordia"),
            ('coreward', 'rimward', "# -5, 4", 'y', "Coreward sector y co-ord mismatch for Fnordia"),
            ('rimward', 'coreward', "# -5, 4", 'y', "Rimward sector y co-ord mismatch for Fnordia"),
            ('spinward', 'trailing', "# -6, 5", 'y', "Spinward sector y co-ord mismatch for Fnordia"),
            ('trailing', 'spinward', "# -4, 5", 'y', "Trailing sector y co-ord mismatch for Fnordia"),
            ('coreward', 'rimward', "# -5, 5", 'true', None),
            ('rimward', 'coreward', "# -5, 3", 'true', None),
            ('spinward', 'trailing', "# -6, 4", 'true', None),
            ('trailing', 'spinward', "# -4, 4", 'true', None),
        ]

        for direction, reverse, rhubarb_posn, co_ord_type, exp_msg in cases:
            with self.subTest(direction + " " + co_ord_type):
                name = "# Fnordia"
                position = "# -5, 4"

                sector = Sector(name, position)

                name = "# Rhubarb"
                rhubarb = Sector(name, rhubarb_posn)

                sector.__setattr__(direction, rhubarb)
                rhubarb.__setattr__(reverse, sector)
                well_formed, msg = sector.is_well_formed()
                if exp_msg is not None:
                    self.assertFalse(well_formed)
                    self.assertEqual(exp_msg, msg)
                else:
                    self.assertTrue(well_formed)
                    self.assertEqual("", msg)

    def test_is_well_formed_subsector_allegiance_mismatch(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)

        subsector = Subsector('Rhubarb', 'A', sector)
        alg = Allegiance('NaHu', 'NaHu', True)
        subsector.alg['NaHu'] = alg
        sector.subsectors['A'] = subsector

        exp_msg = "Allegiance NaHu found in subsector A but not sector"
        well_formed, msg = sector.is_well_formed()
        self.assertFalse(well_formed)
        self.assertEqual(exp_msg, msg)

    def test_is_well_formed_subsector_allegiance_count_mismatch(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)

        subsector = Subsector('Rhubarb', 'A', sector)
        alg = Allegiance('NaHu', 'NaHu', True)
        subsector.alg['NaHu'] = alg
        sector.subsectors['A'] = subsector
        nu_alg = Allegiance('NaHu', 'NaHu', True)
        nu_alg.worlds.append('00')
        self.assertEqual(1, len(nu_alg.worlds))
        self.assertEqual(0, len(alg.worlds))
        sector.alg['NaHu'] = nu_alg

        exp_msg = "Allegiance NaHu has 1 worlds at sector, and 0 totalled across subsectors"
        well_formed, msg = sector.is_well_formed()
        self.assertFalse(well_formed)
        self.assertEqual(exp_msg, msg)

    def test_is_well_formed_allegiance_match(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)

        a_subsector = Subsector('Rhubarb', 'A', sector)
        b_subsector = Subsector('Foobar', 'B', sector)
        sec_alg = Allegiance('NaHu', 'NaHu', True)
        sec_alg.worlds.append('--')
        sec_alg.worlds.append('--')
        a_alg = Allegiance('NaHu', 'NaHu', True)
        a_alg.worlds.append('--')
        b_alg = Allegiance('NaHu', 'NaHu', True)
        b_alg.worlds.append('--')
        self.assertEqual(2, len(sec_alg.worlds))
        a_subsector.alg['NaHu'] = a_alg
        b_subsector.alg['NaHu'] = b_alg
        sector.alg['NaHu'] = sec_alg
        sector.subsectors['A'] = a_subsector
        sector.subsectors['B'] = b_subsector

        well_formed, msg = sector.is_well_formed()
        self.assertTrue(well_formed)
        self.assertEqual('', msg)

    def test_find_world_by_pos(self) -> None:
        name = "# Fnordia"
        position = "# -5, 4"

        sector = Sector(name, position)
        self.assertIsNone(sector.find_world_by_pos('0101'))

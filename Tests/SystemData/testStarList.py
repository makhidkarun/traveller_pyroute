"""
Created on Nov 17, 2025

@author: CyberiaResurrection
"""
import unittest

from PyRoute.SystemData.StarList import StarList


class testStarList(unittest.TestCase):

    def test_9_stars_none_trim(self) -> None:
        star_line = "G1 V G2 V G3 V G4 V G5 V G6 V G7 V G8 V G9 V"
        msg = None
        try:
            StarList(star_line)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Max number of stars is 8", msg)

    def test_9_stars_no_trim(self) -> None:
        star_line = "G1 V G2 V G3 V G4 V G5 V G6 V G7 V G8 V G9 V"
        msg = None
        try:
            StarList(star_line, trim_stars=False)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Max number of stars is 8", msg)

    def test_9_stars_trim(self) -> None:
        star_line = "G1 G2 G3 G4 G5 G6 G7 G8 G9"
        starlist = StarList(star_line, trim_stars=True)

        exp_str = "G1 V G2 V G3 V G4 V G5 V G6 V G7 V G8 V"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)

    def test_1_star_no_space(self) -> None:
        star_line = "G1V"
        starlist = StarList(star_line, trim_stars=True)

        exp_str = "G1 V"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertEqual('G1V', starlist.stars_line)

    def test_no_star_no_space(self) -> None:
        star_line = ""
        starlist = StarList(star_line)

        exp_str = ""
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('', starlist.stars_line)

    def test_dwarf_star_no_space(self) -> None:
        star_line = "D"
        starlist = StarList(star_line)

        exp_str = "D"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('D', starlist.stars_line)

    def test_neutron_star_no_space(self) -> None:
        star_line = "NS"
        starlist = StarList(star_line)

        exp_str = "NS"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('NS', starlist.stars_line)

    def test_pulsar_no_space(self) -> None:
        star_line = "PSR"
        starlist = StarList(star_line)

        exp_str = "PSR"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('PSR', starlist.stars_line)

    def test_black_hole_no_space(self) -> None:
        star_line = "BH"
        starlist = StarList(star_line)

        exp_str = "BH"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('BH', starlist.stars_line)

    def test_brown_dwarf_no_space(self) -> None:
        star_line = "BD"
        starlist = StarList(star_line)

        exp_str = "BD"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)
        self.assertIsNotNone(starlist.stars_line)
        self.assertEqual('BD', starlist.stars_line)

    def test_canonicalise_1(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)
        self.assertEqual("G5 V B2 Ia", str(star_list))
        star_list.canonicalise()
        self.assertEqual("B2 Ia G5 V", str(star_list))

    def test_check_canonical(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)
        self.assertEqual(2, len(star_list.stars_list))

        _, msg = star_list.check_canonical()
        exp_msg = [
            'Star 1 cannot be supergiant - is B2 Ia',
            'Flux values 2 to 8 only permit sizes D IV V of B class star - not Ia'
        ]
        self.assertEqual(exp_msg, msg)

    def test_check_is_well_formed(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)
        self.assertEqual(2, len(star_list.stars_list))

        _, msg = star_list.is_well_formed()
        exp_msg = 'Index 1 better primary candidate than index 0'
        self.assertEqual(exp_msg, msg)

    def test_check_star_size_against_primary(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)

        msg = []
        star_list.check_star_size_against_primary(star_list.stars_list[0], msg)
        exp_msg = []
        self.assertEqual(exp_msg, msg)
        star_list.check_star_size_against_primary(star_list.stars_list[1], msg)
        exp_msg = ['Flux values 2 to 8 only permit sizes D IV V of B class star - not Ia']
        self.assertEqual(exp_msg, msg)

    def test_move_biggest_to_primary(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)

        star_list.move_biggest_to_primary()
        exp_line = "B2 Ia G5 V"
        self.assertEqual(exp_line, str(star_list))

    def test_fix_star_size_against_primary(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)

        star_list.fix_star_size_against_primary(star_list.stars_list[1])
        exp_line = "G5 V B2 V"
        self.assertEqual(exp_line, str(star_list))

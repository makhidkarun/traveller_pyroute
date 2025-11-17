"""
Created on Nov 17, 2025

@author: CyberiaResurrection
"""
import unittest

from PyRoute.SystemData.StarList import StarList
from PyRoute.SystemData.SystemStar import SystemStar


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

    def test_6_stars_trim(self) -> None:
        star_line = "G1 G2 G3 V G4 V G5 G6"
        starlist = StarList(star_line, trim_stars=True)

        exp_str = "G1 V G2 V G3 V G4 V G5 V G6 V"
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)

    def test_1_star_no_space(self) -> None:
        cases = [
            ('G1V', 'G1 V'),
            ('G1III', 'G1 III')
        ]

        for star_line, exp_str in cases:
            starlist = StarList(star_line, trim_stars=True)
            act_str = str(starlist)
            self.assertEqual(exp_str, act_str)
            self.assertEqual(star_line, starlist.stars_line)

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

    def test_v_as_c(self) -> None:
        star_line = 'B2 IC F2 C'
        starlist = StarList(star_line)

        exp_str = 'B2 IV F2 V'
        act_str = str(starlist)
        self.assertEqual(exp_str, act_str)

    def test_canonicalise_1(self) -> None:
        cases = [
            ("G5 V B2 Ia", "G5 V B2 Ia", "B2 Ia G5 V"),
            ("B0 Ib A2 III O5 II", "B0 Ib A2 III O5 II", "B0 Ib A2 IV O5 III"),
            ("B0 Ib B2 II A2 II", "B0 Ib B2 II A2 II", "B0 Ib B2 III A2 IV"),
            ('O6 Ib F2 III G0 II K0 IV M5 IV', 'O6 Ib F2 III G0 II K0 IV M5 IV', 'O6 Ib F2 V G0 V K0 V M5 V'),
            ('O0 Ia O9 Ib B9 Ib A9 Ib F9 Ib G9 Ib K9 Ib M9 Ib', 'O0 Ia O9 Ib B9 Ib A9 Ib F9 Ib G9 Ib K9 Ib M9 Ib',
             'O0 Ia O9 II B9 II A9 II F9 IV G9 IV K9 V M9 II'),
            ('B3 Ib B4 IV O4 IV A4 V', 'B3 Ib B4 IV O4 IV A4 V', 'B3 Ib B4 V O4 V A4 V'),
            ('O0 Ia K3 II K4 II K5 II K6 II', 'O0 Ia K3 II K4 II K5 II K6 II', 'O0 Ia K3 IV K4 V K5 V K6 V'),
            ('O0 Ia K3 III K4 III K5 III K6 III', 'O0 Ia K3 III K4 III K5 III K6 III', 'O0 Ia K3 IV K4 V K5 V K6 V'),
            ('O9 Ia F3 II F4 II', 'O9 Ia F3 II F4 II', 'O9 Ia F3 IV F4 IV'),
            ('O9 Ia G3 III', 'O9 Ia G3 III', 'O9 Ia G3 IV'),
            ('B9 Ia G3 III', 'B9 Ia G3 III', 'B9 Ia G3 IV'),
            ('A9 Ia G3 III', 'A9 Ia G3 III', 'A9 Ia G3 V'),
            ('A0 Ia K3 II K4 II K5 II K6 II', 'A0 Ia K3 II K4 II K5 II K6 II', 'A0 Ia K3 V K4 V K5 V K6 V'),
            ('A0 Ib K3 II K4 II K5 II K6 II', 'A0 Ib K3 II K4 II K5 II K6 II', 'A0 Ib K3 V K4 V K5 V K6 V'),
            ('A0 II K3 II K4 II K5 II K6 II', 'A0 II K3 II K4 II K5 II K6 II', 'A0 II K3 V K4 V K5 V K6 V'),
            ('A0 Ib F4 III G4 III K4 III M4 III', 'A0 Ib F4 III G4 III K4 III M4 III', 'A0 Ib F4 V G4 V K4 V M4 V'),
            ('A0 Ib F4 IV G4 IV K4 IV M4 IV', 'A0 Ib F4 IV G4 IV K4 IV M4 IV', 'A0 Ib F4 V G4 V K4 V M4 V'),
            ('A0 Ib PSR', 'A0 Ib PSR', 'A0 Ib PSR')
        ]

        for star_line, exp_list, exp_canonical in cases:
            with self.subTest(star_line):
                star_list = StarList(star_line)
                self.assertEqual(exp_list, str(star_list))
                star_list.canonicalise()
                self.assertEqual(exp_canonical, str(star_list))

    def test_check_canonical(self) -> None:
        cases = [
            ("G5 V B2 Ia", 2,
             [
                 'Star 1 cannot be supergiant - is B2 Ia',
                 'Flux values 2 to 8 only permit sizes D IV V of B class star - not Ia'
             ]
             ),
            ('B2 Ib PSR', 2, []),
            ('O2 Ib O6 II B6 II A4 II A5 III', 5,
             [
                 'Ib supergiant primary precludes O-class bright giants - size II - is O6 II',
                 'Ib supergiant primary precludes B-class bright giants - size II - is B6 II',
                 'Ib supergiant primary precludes A-class bright and regular giants - size II and III - is A4 II',
                 'Ib supergiant primary precludes A-class bright and regular giants - size II and III - is A5 III'
             ]),
            ('O2 Ib F3 II', 2, [
                'Supergiant primary precludes F-class with sizes II and III - bright and regular giants - is F3 II',
                'Ib supergiant primary precludes F-class bright, regular and subgiants - size II, III and IV - is F3 II',
                'Flux values -3 to 2 only permit sizes IV V of F0-4 class star - not II'
            ]),
            ('O2 Ib F5 II', 2, [
                'Supergiant primary precludes F-class with sizes II and III - bright and regular giants - is F5 II',
                'Ib supergiant primary precludes F-class bright, regular and subgiants - size II, III and IV - is F5 II',
                'Flux values -3 to 2 only permit sizes IV V of F5-9 class star - not II'
            ]),
            ('O2 Ib G3 II', 2, [
                'Supergiant primary precludes G-class with sizes II and III - bright and regular giants - is G3 II',
                'Ib supergiant primary precludes G-class bright, regular and subgiants - size II, III and IV - is G3 II',
                'Flux values -3 to 2 only permit sizes IV V of G class star - not II'
            ]),
            ('O2 Ib K3 II', 2, [
                'Supergiant primary precludes K-class with sizes II and III - bright and regular giants - is K3 II',
                'Ib supergiant primary precludes K-class bright, regular and subgiants - size II, III and IV - is K3 II',
                'Flux values -3 to 2 only permit sizes IV V of K class star - not II'
            ]),
            ('O2 Ib K3 III', 2, [
                'Supergiant primary precludes K-class with sizes II and III - bright and regular giants - is K3 III',
                'Ib supergiant primary precludes K-class bright, regular and subgiants - size II, III and IV - is K3 III',
                'Flux values -3 to 2 only permit sizes IV V of K class star - not III'
            ]),
            ('O2 Ib M3 II', 2, [
                'Ib supergiant primary precludes M-class bright, regular and subgiants - size II, III and IV - is M3 II'
            ]),
            ('O2 Ia D', 2, [
                'Supergiant primary precludes D-class stars'
            ])
        ]

        for star_line, exp_stars, exp_msg in cases:
            with self.subTest(star_line):
                star_list = StarList(star_line)
                self.assertEqual(exp_stars, len(star_list.stars_list))
                result, msg = star_list.check_canonical()
                self.assertEqual(0 == len(msg), result)
                self.assertEqual(exp_msg, msg)

    def test_check_is_well_formed(self) -> None:
        star_line = "G5 V B2 Ia"
        star_list = StarList(star_line)
        self.assertEqual(2, len(star_list.stars_list))

        result, msg = star_list.is_well_formed()
        exp_msg = 'Index 1 better primary candidate than index 0'
        self.assertFalse(result)
        self.assertEqual(exp_msg, msg)

    def test_check_is_well_formed_too_many_stars(self) -> None:
        star_line = "G1 G2 G3 G4 G5 G6 G7 G8 G9"
        star_list = StarList(star_line, trim_stars=True)
        self.assertEqual(8, len(star_list.stars_list))

        nustar = SystemStar('D')
        star_list.stars_list.append(nustar)
        result, msg = star_list.is_well_formed()
        exp_msg = 'Max stars exceeded'
        self.assertFalse(result)
        self.assertEqual(exp_msg, msg)

    def test_check_is_well_formed_non_system_star(self) -> None:
        star_line = "G1 G2 G3 G4 G5 G6 G7"
        star_list = StarList(star_line, trim_stars=True)
        self.assertEqual(7, len(star_list.stars_list))

        nustar = 'SystemStar'
        star_list.stars_list.append(nustar)
        result, msg = star_list.is_well_formed()
        exp_msg = 'Item SystemStar not a SystemStar'
        self.assertFalse(result)
        self.assertEqual(exp_msg, msg)

    def test_check_is_well_formed_three_identical_stars(self) -> None:
        star_line = "O5 Ia O5 Ia O5 Ia"
        star_list = StarList(star_line, trim_stars=True)
        self.assertEqual(3, len(star_list.stars_list))

        result, msg = star_list.is_well_formed()
        exp_msg = ''
        self.assertTrue(result)
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
        cases = [
            ("G5 V B2 Ia G5 V", "B2 Ia G5 V G5 V"),
            ("O0 Ib O0 Ia", 'O0 Ia O0 Ib')
        ]

        for star_line, exp_line in cases:
            with self.subTest(star_line):
                star_list = StarList(star_line)
                star_list.move_biggest_to_primary()
                self.assertEqual(exp_line, str(star_list))

    def test_fix_star_size_against_primary(self) -> None:
        cases = [
            ("G5 V B2 Ia", "G5 V B2 V"),
            ('D A5 Ib', 'D A5 Ib'),
            ('B5 Ia F4 II', 'B5 Ia F4 IV'),
            ('B5 Ia F4 III', 'B5 Ia F4 IV'),
            ('B5 Ia F4 IV', 'B5 Ia F4 IV'),
            ('B5 Ia F4 V', 'B5 Ia F4 V'),
            ('B5 Ia F4 VI', 'B5 Ia F4 IV'),
            ('B5 Ia K4 II', 'B5 Ia K4 IV'),
            ('B5 Ia F5 II', 'B5 Ia F5 IV'),
            ('B5 Ia K5 II', 'B5 Ia K5 V'),
            ('B5 Ia F6 II', 'B5 Ia F6 IV'),
            ('B5 Ia K6 II', 'B5 Ia K6 V'),
            ('M0 V M9 IV', 'M0 V M9 VI'),
        ]

        for star_line, exp_line in cases:
            with self.subTest(star_line):
                star_list = StarList(star_line)

                star_list.fix_star_size_against_primary(star_list.stars_list[1])
                self.assertEqual(exp_line, str(star_list))

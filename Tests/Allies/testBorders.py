"""
Created on Apr 17, 2025

@author: CyberiaResurrection
"""
from collections import defaultdict
from logging import Logger
from unittest.mock import patch

from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Allies.Borders import Borders
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute import Star
from Tests.baseTest import baseTest


class testBorders(baseTest):
    def test_init(self) -> None:
        galaxy: Galaxy = Galaxy(0)
        borders: Borders = galaxy.borders
        self.assertIsInstance(borders.galaxy, Galaxy)
        self.assertEqual({}, borders.borders)
        self.assertEqual({}, borders.borders_map)
        self.assertEqual({}, borders.allyMap)
        logger = borders.logger
        self.assertIsInstance(logger, Logger)
        self.assertEqual('PyRoute.Borders', logger.name)

    def test_is_well_formed(self) -> None:
        galaxy = Galaxy(0)
        borders = galaxy.borders
        well_formed, msg = borders.is_well_formed()
        self.assertTrue(well_formed)
        self.assertEqual("", msg)

    def test_ally_map_x_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            X9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(0, 36): ['red', 'red', None], (0, 37): ['red', None, 'red'], (1, 35): [None, 'red', None],
                       (1, 36): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(0, 37): 'Im'})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_x_port_diff_q(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0204 Irkigkhan            X9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(1, 34): ['red', 'red', 'red'], (1, 35): ['red', None, None], (2, 34): [None, 'red', 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(1, 35): 'Im'})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_e_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            E9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(0, 36): ['red', 'red', None], (0, 37): ['red', None, 'red'], (1, 35): [None, 'red', None],
                       (1, 36): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(0, 37): 'Im'})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_d_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            D9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(0, 36): ['red', 'red', None], (0, 37): ['red', None, 'red'], (1, 35): [None, 'red', None],
                       (1, 36): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(-1, 37): None, (-1, 38): None, (0, 36): None, (0, 37): 'Im',
                                 (0, 38): None, (1, 36): None, (1, 37): None})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_c_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(-2, 36): ['red', 'red', None], (-2, 37): [None, 'red', 'red'], (-2, 38): ['red', None, 'red'],
                        (-1, 35): [None, 'red', None], (-1, 36): ['red', None, None], (-1, 37): [None, 'red', None],
                        (-1, 38): ['red', None, None], (0, 35): ['red', 'red', None], (0, 37): ['red', 'red', None],
                        (1, 34): [None, 'red', None], (1, 35): [None, 'red', 'red'], (1, 36): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(-2, 37): 'Im',
             (-2, 38): 'Im', (-2, 39): None, (-1, 36): None, (-1, 37): 'Im', (-1, 38): 'Im', (-1, 39): None,
             (0, 35): None, (0, 36): 'Im', (0, 37): 'Im', (0, 38): None, (0, 39): None, (1, 35): None, (1, 36): None,
             (1, 37): None, (1, 38): None, (2, 35): None, (2, 36): None, (2, 37): None})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_b_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            B9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(-3, 36): ['red', 'red', 'red'], (-3, 37): [None, 'red', 'red'], (-3, 38): [None, 'red', 'red'],
                        (-3, 39): [None, 'red', 'red'], (-3, 40): ['red', None, None], (-2, 35): ['red', 'red', None],
                        (-2, 40): ['red', None, 'red'], (-1, 34): [None, 'red', None], (-1, 35): ['red', None, None],
                        (-1, 39): ['red', None, 'red'], (0, 34): ['red', 'red', None], (0, 38): ['red', 'red', None],
                        (1, 33): [None, 'red', None], (1, 34): ['red', None, None], (1, 37): ['red', None, 'red'],
                        (2, 34): [None, 'red', 'red'], (2, 35): [None, 'red', 'red'], (2, 36): [None, 'red', 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (-2, 37): 'Im', (-3, 37): 'Im', (-3, 38): 'Im', (-3, 39): 'Im', (-3, 40): 'Im', (-2, 36): 'Im',
            (-2, 38): 'Im', (-2, 39): 'Im', (-2, 40): 'Im', (-1, 35): None, (-1, 36): 'Im',
            (-1, 37): 'Im', (-1, 38): 'Im', (-1, 39): 'Im', (-1, 40): None, (0, 34): None, (0, 35): 'Im',
            (0, 36): 'Im', (0, 37): 'Im', (0, 38): 'Im', (0, 39): None, (0, 40): None, (1, 34): None, (1, 35): 'Im',
            (1, 36): 'Im', (1, 37): 'Im', (1, 38): None, (1, 39): None, (2, 34): None, (2, 35): None, (2, 36): None,
            (2, 37): None, (2, 38): None, (3, 34): None, (3, 35): None, (3, 36): None, (3, 37): None})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_a_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            A9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {(-4, 36): ['red', 'red', None], (-4, 37): [None, 'red', 'red'], (-4, 38): [None, 'red', 'red'],
                        (-4, 39): [None, 'red', 'red'], (-4, 40): [None, 'red', 'red'], (-4, 41): ['red', None, 'red'],
                        (-3, 35): ['red', None, 'red'], (-3, 40): [None, 'red', None], (-3, 41): ['red', None, None],
                        (-2, 34): ['red', 'red', None], (-2, 41): ['red', None, 'red'], (-1, 33): [None, 'red', None],
                        (-1, 34): ['red', None, None], (-1, 40): ['red', None, 'red'], (0, 33): ['red', 'red', None],
                        (0, 39): ['red', 'red', None], (1, 32): [None, 'red', None], (1, 33): ['red', None, None],
                        (1, 38): ['red', None, 'red'], (2, 33): ['red', None, 'red'], (2, 37): ['red', 'red', None],
                        (3, 32): [None, 'red', None], (3, 33): [None, 'red', 'red'], (3, 34): [None, 'red', 'red'],
                        (3, 35): [None, 'red', 'red'], (3, 36): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (-4, 37): 'Im', (-4, 38): 'Im', (-4, 39): 'Im', (-4, 40): 'Im', (-4, 41): 'Im', (-3, 36): 'Im',
            (-3, 37): 'Im', (-3, 38): 'Im', (-3, 39): 'Im', (-3, 40): 'Im', (-3, 41): 'Im', (-2, 35): 'Im',
            (-2, 36): 'Im', (-2, 37): 'Im', (-2, 38): 'Im', (-2, 39): 'Im', (-2, 40): 'Im', (-2, 41): 'Im',
            (-1, 34): None, (-1, 35): 'Im', (-1, 36): 'Im', (-1, 37): 'Im', (-1, 38): 'Im', (-1, 39): 'Im',
            (-1, 40): 'Im', (-1, 41): None, (0, 33): None, (0, 34): 'Im', (0, 35): 'Im', (0, 36): 'Im',
            (0, 37): 'Im', (0, 38): 'Im', (0, 39): 'Im', (0, 40): None, (0, 41): None, (1, 33): None,
            (1, 34): 'Im', (1, 35): 'Im', (1, 36): 'Im', (1, 37): 'Im', (1, 38): 'Im', (1, 39): None,
            (1, 40): None, (2, 33): None, (2, 34): 'Im', (2, 35): 'Im', (2, 36): 'Im', (2, 37): 'Im',
            (2, 38): None, (2, 39): None, (3, 33): None, (3, 34): None, (3, 35): None, (3, 36): None,
            (3, 37): None, (3, 38): None, (4, 33): None, (4, 34): None, (4, 35): None, (4, 36): None,
            (4, 37): None})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_na_port(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            E9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Na M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {(-1, 37): None, (-1, 38): None, (0, 36): None, (0, 37): 'Na', (0, 38): None,
                                        (1, 36): None, (1, 37): None})

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_two_different_allegiances_one_droyne(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Zdiedeiant', '# -7,3')

        star1 = Star.parse_line_into_star(
            '0332 Plit-79              D252000-0 Ba Po                               - -  R 020   ZhIa        ',
            sector, 'fixed', 'fixed'
        )
        star1.index = 0
        galaxy.star_mapping[0] = star1
        star2 = Star.parse_line_into_star(
            '0432 Uevro                C3515X6-9 Ni Po                               - -  R 322   Dr          ',
            sector, 'fixed', 'fixed'
        )
        star2.index = 1
        galaxy.star_mapping[1] = star2
        galaxy.alg['Dr'] = Allegiance('Dr', 'Droyne', True, 'Droy')
        galaxy.alg['Dr'].stats.numbers = 1
        galaxy.alg['ZhIa'] = Allegiance('ZhIa', 'Zhodani Consulate', False, 'Zhod')
        galaxy.alg['ZhIa'].stats.numbers = 1

        borders = galaxy.borders
        borders.create_ally_map('')
        exp_borders = {
            (-222, 237): [None, None, None], (-222, 238): ['white', 'white', None],
            (-222, 239): ['white', None, 'white'], (-221, 236): [None, None, None],
            (-221, 237): [None, 'white', None], (-221, 238): [None, None, 'white'],
            (-221, 239): [None, None, None], (-220, 236): [None, None, None],
            (-220, 237): [None, None, None], (-220, 238): [None, None, None]
        }
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (-223, 238): None, (-223, 239): None, (-223, 240): None, (-222, 237): None, (-222, 238): 'Dr',
            (-222, 239): 'ZhIa', (-222, 240): None, (-221, 236): None, (-221, 237): 'Dr', (-221, 238): 'Dr',
            (-221, 239): 'Dr', (-221, 240): None, (-220, 236): None, (-220, 237): None, (-220, 238): None,
            (-220, 239): None, (-219, 236): None, (-219, 237): None, (-219, 238): None
        })

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_six_different_allegiances_around_blank(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Zdiedeiant', '# -7,3')
        star1 = Star.parse_line_into_star(
            '0332 Plit-79              E252000-0 Ba Po                               - -  R 020   ZhIa        ',
            sector, 'fixed', 'fixed'
        )
        star1.index = 0
        galaxy.star_mapping[0] = star1
        star2 = Star.parse_line_into_star(
            '0532 Uevro                E3515X6-9 Ni Po                               - -  R 322   ZhIN          ',
            sector, 'fixed', 'fixed'
        )
        star2.index = 1
        galaxy.star_mapping[1] = star2
        star3 = Star.parse_line_into_star(
            '0433 Plit-79              E252000-0 Ba Po                               - -  R 020   Zh          ',
            sector, 'fixed', 'fixed'
        )
        star3.index = 2
        galaxy.star_mapping[2] = star3
        star4 = Star.parse_line_into_star(
            '0431 Uevro                E3515X6-9 Ni Po                               - -  R 322   CsZh          ',
            sector, 'fixed', 'fixed'
        )
        star4.index = 3
        galaxy.star_mapping[3] = star4
        star5 = Star.parse_line_into_star(
            '0333 Plit-79              E252000-0 Ba Po                               - -  R 020   ZhVq        ',
            sector, 'fixed', 'fixed'
        )
        star5.index = 4
        galaxy.star_mapping[4] = star5
        star6 = Star.parse_line_into_star(
            '0533 Uevro                E3515X6-9 Ni Po                               - -  R 322   ZhCh          ',
            sector, 'fixed', 'fixed'
        )
        star6.index = 5
        galaxy.star_mapping[5] = star6

        galaxy.alg['ZhIN'] = Allegiance('ZhIN', 'Zhodani Consulate', False, 'Zhod')
        galaxy.alg['ZhIN'].stats.numbers = 1
        galaxy.alg['ZhIa'] = Allegiance('ZhIa', 'Zhodani Consulate', False, 'Zhod')
        galaxy.alg['ZhIa'].stats.numbers = 1
        galaxy.alg['Zh'] = Allegiance('Zh', 'Zhodani Consulate', True, 'Zhod')
        galaxy.alg['Zh'].stats.numbers = 1
        galaxy.alg['CsZh'] = Allegiance('CsZh', 'Client state, Zhodani Consulate', False, 'Zhod')
        galaxy.alg['CsZh'].stats.numbers = 1
        galaxy.alg['ZhVq'] = Allegiance('ZhVq', 'Zhodani Consulate', False, 'Zhod')
        galaxy.alg['ZhVq'].stats.numbers = 1
        galaxy.alg['ZhCh'] = Allegiance('ZhCh', 'Zhodani Consulate', False, 'Zhod')
        galaxy.alg['ZhCh'].stats.numbers = 1

        borders = galaxy.borders
        borders.create_ally_map('separate')
        exp_borders = {
            (-222, 237): ['white', 'white', None], (-222, 238): ['white', 'white', 'white'],
            (-222, 239): ['white', None, 'white'], (-221, 236): ['blue', 'white', 'blue'],
            (-221, 237): ['white', 'white', 'white'], (-221, 238): ['white', None, 'white'],
            (-220, 236): ['white', 'white', 'blue'], (-220, 237): ['white', 'white', None],
            (-220, 238): ['white', None, 'white'], (-219, 235): [None, 'white', None],
            (-219, 236): [None, 'white', 'white'], (-219, 237): [None, None, 'white']
        }
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (-222, 238): 'ZhVq',
            (-222, 239): 'ZhIa',
            (-222, 240): None,
            (-221, 237): 'Zh',
            (-221, 238): 'ZhCh',
            (-221, 239): 'Na',
            (-221, 240): None,
            (-220, 237): 'ZhCh',
            (-220, 238): 'ZhIN',
            (-220, 239): None
        })

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_ally_map_one_noone_world(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Zdiedeiant', '# -7,3')
        star1 = Star.parse_line_into_star(
            '0332 Plit-79              X252000-0 Ba Po                               - -  R 020   --        ',
            sector, 'fixed', 'fixed'
        )
        star1.index = 0
        galaxy.star_mapping[0] = star1
        borders = galaxy.borders
        borders.create_ally_map('separate')
        exp_borders = {
        }
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (-223, 239): None, (-223, 240): None, (-222, 238): None,
            (-222, 239): 'Na', (-222, 240): None, (-221, 238): None,
            (-221, 239): None
        })
        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_erode_a_ports(self) -> None:
        galaxy = Galaxy(0)
        sector = Sector('# Core', '# 0, 0')
        star1 = Star.parse_line_into_star(
            "0103 Irkigkhan            A9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 0
        galaxy.star_mapping[0] = star1

        star2 = Star.parse_line_into_star(
            "0303 Irkigkhan            A9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           ",
            sector, 'fixed', 'fixed')
        star1.index = 1
        galaxy.star_mapping[1] = star2

        borders = galaxy.borders
        borders.create_erode_border('separate')
        exp_borders = {(0, 36): ['red', 'red', None], (0, 37): ['red', None, 'red'], (1, 35): [None, 'red', None],
                       (1, 36): [None, None, 'red'], (2, 35): ['red', 'red', None], (2, 36): ['red', None, 'red'],
                       (3, 34): [None, 'red', None], (3, 35): [None, None, 'red']}
        exp_borders_map = {}
        exp_allymap = defaultdict(set, {
            (0, 37): 'Im', (2, 36): 'Im'
        })

        self.assertEqual(exp_borders, borders.borders)
        self.assertEqual(exp_borders_map, borders.borders_map)
        self.assertEqual(exp_allymap, borders.allyMap)
        result, msg = borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_break_spans(self) -> None:
        cases = [
            ({}, {}, False, {}),
            ({}, {(0, 36): 'Im', (-1, 36): 'Im', (-2, 36): 'Im', (-3, 36): 'Im'},
             True, {(0, 36): 'Im', (-1, 36): None, (-2, 36): 'Im', (-3, 36): 'Im'})
        ]

        for starmap, allymap, exp_changed, exp_allymap in cases:
            galaxy = Galaxy(0)
            borders = galaxy.borders
            changed, act_allymap = borders._break_spans(allymap, starmap)
            self.assertIsNotNone(changed, "Boolean flag must not be None")
            self.assertEqual(exp_changed, changed, "Unexpected changed value")
            self.assertEqual(exp_allymap, act_allymap, "Unexpected ally-map value")

    def test_erode_too_much_change(self) -> None:
        galaxy = Galaxy(0)
        borders = galaxy.borders

        logger = borders.logger
        logger.manager.disable = 0

        with patch.object(borders, '_erode', return_value=(True, {})) as mock_method, self.assertLogs(logger, 'DEBUG')\
                as logs:
            borders.create_erode_border('separate')
            mock_method.assert_called()
            exp_output = [
                'INFO:PyRoute.Borders:Processing worlds for erode map drawing',
                'ERROR:PyRoute.Borders:Change count for map processing exceeded expected value of 100',
                'DEBUG:PyRoute.Borders:Change Count: 100'
            ]
            self.assertEqual(exp_output, logs.output)

    def test_erode(self) -> None:
        cases = [
                    ({}, {}, False, {}),
                    ({(0, 36): 'Im', (1, 35): 'Im', (1, 36): 'Im', (0, 37): 'Im'}, {},
                     True, {}),
                    ({(0, 36): 'Sc', (1, 35): 'Im', (1, 36): 'Im', (0, 37): 'Im', (-1, 36): 'Im', (0, 38): 'Im',
                      (-2, 38): 'Im', (-2, 36): 'Im', (2, 34): 'Im', (2, 36): 'Im'}, {(0, 36): 'Sc'},
                     True, {(0, 36): 'Sc', (1, 36): 'Im'})
                ]

        for allymap, starmap, exp_changed, exp_allymap in cases:
            galaxy = Galaxy(0)
            borders = galaxy.borders
            act_changed, act_allymap = borders._erode(allymap, starmap)
            self.assertIsNotNone(act_changed, 'Boolean flag should not be None')
            self.assertEqual(exp_changed, act_changed, "Unexpected changed value")
            self.assertEqual(exp_allymap, act_allymap, 'Unexpected ally_map result')

    def test_erode_map(self) -> None:
        cases = [
                    ([], 'separate', defaultdict(set, {}), {}, []),
                    ([], 'collapse', defaultdict(set, {}), {}, []),
            (
                [
                    "0103 Irkigkhan            D9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V",
                    "0303 Shana Ma             D551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Zh K2 IV M7 V"
                ], "separate", defaultdict(set, {(-1, 37): 'Im', (-1, 38): 'Im', (0, 36): 'Im', (0, 37): 'Im',
                                        (0, 38): 'Im', (1, 36): 'Im', (1, 37): 'Im', (2, 35): 'Zh', (2, 36): 'Zh',
                                        (2, 37): 'Zh', (3, 35): 'Zh', (3, 36): 'Zh'}), {(0, 37): 'Im', (2, 36): 'Zh'},
                ['Im', 'Zh']
            ),
            (
                ["0103 Irkigkhan            D9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Na M2 V",
                    "0303 Shana Ma             D551112-7 Lo Po                { -3 } (301-3) [1113] B     - - 913 9  Na K2 IV M7 V"
                ], "separate", defaultdict(set, {(0, 37): 'Na', (2, 36): 'Na'}), {(0, 37): 'Na', (2, 36): 'Na'},
                ['Na']
            ),
            (
                ["0103 Irkigkhan            D9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Na M2 V"],
                'separate', defaultdict(set, {(0, 37): 'Na'}), {(0, 37): 'Na'}, ['Na']
            ),
            (
                ["0103 Irkigkhan            E9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V"],
                'separate', defaultdict(set, {(0, 37): 'Im'}), {(0, 37): 'Im'}, ['Im']
            ),
            (
                ["0103 Irkigkhan            ?9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V"],
                'separate', defaultdict(set, {(0, 37): 'Im'}), {(0, 37): 'Im'}, ['Im']
            ),
            (
                ["0103 Irkigkhan            X9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V"],
                'separate', defaultdict(set, {(0, 37): 'Im'}), {(0, 37): 'Im'}, ['Im']
            ),
            (
                ["0103 Irkigkhan            D9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  -- M2 V"],
                'separate', defaultdict(set, {(0, 37): 'Na'}), {(0, 37): 'Na'}, ['--']
            )
            ]

        for stars_list, match, exp_allymap, exp_starmap, alg_list in cases:
            with self.subTest():
                galaxy = Galaxy(0)
                sector = Sector('# Core', '# 0, 0')

                counter = -1
                for item in stars_list:
                    star = Star.parse_line_into_star(item, sector, 'fixed', 'fixed')
                    if star is None:
                        continue
                    counter += 1
                    star.index = counter
                    galaxy.star_mapping[counter] = star
                    alg = star.alg_code
                    if alg not in galaxy.alg:
                        galaxy.alg[alg] = Allegiance(alg, alg)
                    galaxy.alg[alg].stats.number += 1

                self.assertEqual(alg_list, list(galaxy.alg.keys()))

                act_allymap, act_starmap = galaxy.borders._erode_map(match)
                self.assertEqual(exp_allymap, act_allymap, "Unexpected allymap value")
                self.assertEqual(exp_starmap, act_starmap, "Unexpected starmap value")

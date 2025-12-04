"""
Created on Apr 17, 2025

@author: CyberiaResurrection
"""
from collections import defaultdict
from logging import Logger

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

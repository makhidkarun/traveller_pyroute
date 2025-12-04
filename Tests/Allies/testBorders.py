"""
Created on Apr 17, 2025

@author: CyberiaResurrection
"""
from logging import Logger

from PyRoute.Allies.Borders import Borders
from PyRoute.AreaItems.Galaxy import Galaxy
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

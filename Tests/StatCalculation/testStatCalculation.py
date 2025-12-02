"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.StatCalculation.StatCalculation import StatCalculation
from Tests.baseTest import baseTest


class testStatCalculation(baseTest):

    def test_init(self) -> None:
        galaxy = Galaxy(8, 4)

        stat = StatCalculation(galaxy)
        logger = stat.logger
        self.assertEqual('PyRoute.StatCalculation', logger.name)

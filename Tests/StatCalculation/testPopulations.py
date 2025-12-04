"""
Created on Dec 03, 2025

@author: CyberiaResurrection
"""
from PyRoute.StatCalculation.Populations import Populations
from Tests.baseTest import baseTest


class testPopulations(baseTest):

    def test_init(self) -> None:
        pop = Populations()
        self.assertEqual("", pop.code)
        self.assertEqual([], pop.homeworlds)
        self.assertEqual(0, pop.count)
        self.assertEqual(0, pop.population)

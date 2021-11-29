"""
Created on Nov 30, 2021

@author: CyberiaResurrection
"""

import unittest
import re
import sys

sys.path.append('../PyRoute')

from Galaxy import Galaxy
from Galaxy import Sector


class testGalaxy(unittest.TestCase):

    """
    A very simple, barebones test to check that Verge and Reft end up in their correct relative positions
    - Verge being immediately rimward of Reft
    """
    def testVerticalOrdering(self):
        galaxy = Galaxy(0)

        reft = Sector("Reft", "# -3, 0")
        self.assertEqual(-3, reft.x)
        self.assertEqual(0, reft.y)

        verge = Sector("Verge", "# -3, -1")
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

"""
Created on Dec 15, 2025

@author: CyberiaResurrection
"""
import unittest

from PyRoute.SystemData.Utilities import Utilities


class testUtilities(unittest.TestCase):

    def test_ehex_to_int_bad_value(self) -> None:
        msg = None
        try:
            Utilities.ehex_to_int(None)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Value must be string", msg)

    def test_int_to_ehex_bad_value(self) -> None:
        msg = None
        try:
            Utilities.int_to_ehex(None)
        except ValueError as e:
            msg = str(e)
        self.assertEqual("Value must be integer", msg)

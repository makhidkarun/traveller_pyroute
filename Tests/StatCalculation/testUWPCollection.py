"""
Created on Dec 03 2025

@author: CyberiaResurrection
"""
from PyRoute.StatCalculation.UWPCollection import UWPCollection
from Tests.baseTest import baseTest


class testUWPCollection(baseTest):

    def test_setitem_1(self) -> None:
        collection = UWPCollection()

        collection['Starport'] = {'A': 1}
        actual = collection['Starport']
        self.assertEqual({'A': 1}, actual)

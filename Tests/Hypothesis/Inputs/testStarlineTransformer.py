"""
Created on Jan 02, 2024

@author: CyberiaResurrection
"""

import unittest

from PyRoute.Inputs.StarlineTransformer import StarlineTransformer


class testStarlineTransformer(unittest.TestCase):
    def test_boil_down_double_spaces(self):
        original = '{   2}'
        expected = '{ 2}'
        actual = StarlineTransformer.boil_down_double_spaces(original)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

"""
Created on Aug 11, 2023

@author: CyberiaResurrection
"""

import unittest

from PyRoute.Calculation.LandmarkData import LandmarkData


class MyTestCase(unittest.TestCase):
    def test_add_distance(self):
        foo = LandmarkData(10)

        foo.add_distance('Foobar', 10)
        self.assertEqual(1, foo.counter)
        self.assertEqual(['Foobar'], foo.tracking[0]['star'])
        self.assertEqual([10], foo.tracking[0]['distance'])

    def test_get_bounds(self):
        foo = LandmarkData(10)

        foo.add_distance('Foo', 10)
        foo.add_distance('Bar', 4)

        expected = [('Foo', 10)]
        actual = foo.get_bounds(5, 3)

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

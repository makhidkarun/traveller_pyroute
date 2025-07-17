"""
Created on Jan 1, 2019

@author: CyberiaResurrection
"""

import unittest

from Nobles import Nobles


class TestNobles(unittest.TestCase):
    def testDefaultString(self) -> None:
        nobles = Nobles()
        expected = '-'
        self.assertEqual(expected, nobles.__str__())

    def testStringWithOneViscount(self) -> None:
        nobles = Nobles()
        nobles.nobles['Viscounts'] = 1

        expected = 'e'
        self.assertEqual(expected, nobles.__str__())

    def testCountWithViscount(self) -> None:
        nobles = Nobles()
        nobles.count(['e'])

        expected = 1
        actual = nobles.nobles['Viscounts']

        self.assertEqual(expected, actual)

    def testAccumulateSelf(self) -> None:
        nobles = Nobles()
        nobles.nobles['Viscounts'] = 1

        nobles.accumulate(nobles)

        expected = 2
        actual = nobles.nobles['Viscounts']

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

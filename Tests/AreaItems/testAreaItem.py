"""
Created on Nov 27, 2025

@author: CyberiaResurrection
"""

import unittest

from PyRoute.AreaItems.AreaItem import AreaItem


class testAreaItem(unittest.TestCase):
    def test_init(self) -> None:
        foo = AreaItem('foobar')
        self.assertEqual('foobar', foo.name)
        self.assertEqual([], foo.worlds)
        self.assertEqual({}, foo.alg)
        self.assertEqual([], foo.alg_sorted)
        self.assertFalse(foo.debug_flag)
        self.assertEqual('foobar', str(foo))

    def test_is_well_formed(self) -> None:
        foo = AreaItem('foobar')
        well_formed, msg = foo.is_well_formed()
        self.assertTrue(well_formed)
        self.assertEqual("", msg)


if __name__ == '__main__':
    unittest.main()

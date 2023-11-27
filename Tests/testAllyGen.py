import unittest

from PyRoute.AllyGen import AllyGen
from PyRoute.Galaxy import Allegiance


class testAllyGen(unittest.TestCase):
    def test_is_nonaligned_no_one(self):
        self.assertTrue(AllyGen.is_nonaligned('??'))

    def test_is_nonaligned_nadr(self):
        self.assertTrue(AllyGen.is_nonaligned('NaDr'))

    def test_is_nonaligned_nahu(self):
        self.assertTrue(AllyGen.is_nonaligned('NaHu'))

    def test_are_allies_one_none(self):
        self.assertFalse(AllyGen.are_allies(None, 'ImDd'))

    def test_are_allies_one_no_one(self):
        self.assertFalse(AllyGen.are_allies('--', 'ImDd'))

    def test_are_owned_allies_one_none(self):
        self.assertFalse(AllyGen.are_owned_allies(None, 'ImDd'))

    def test_are_owned_allies_one_no_one(self):
        self.assertFalse(AllyGen.are_owned_allies('--', 'ImDd'))

    def test_are_owned_allies_same_parent(self):
        self.assertTrue(AllyGen.are_owned_allies('ZhAx', 'ZhCa'))

    def test_are_owned_allies_diff_parent(self):
        self.assertFalse(AllyGen.are_owned_allies('ZhAx', 'HvFd'))

    def test_zhodani_in_name_of_population_alignment(self):
        expected = 'Zhod'
        actual = AllyGen.population_align('Na', 'Zhodani')
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.Allies.AllyGen import AllyGen


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

    def test_is_wilds_none(self):
        expected = False
        actual = AllyGen.is_wilds(None)
        self.assertEqual(expected, actual)

    def test_is_wilds_single_char(self):
        expected = False
        actual = AllyGen.is_wilds('a')
        self.assertEqual(expected, actual)

    def test_is_client_state_none(self):
        expected = False
        actual = AllyGen.is_client_state(None)
        self.assertEqual(expected, actual)

    def test_is_client_state_single_char(self):
        expected = False
        actual = AllyGen.is_client_state('a')
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

import unittest

from PyRoute.SystemData.SystemStar import SystemStar


class testSystemStar(unittest.TestCase):

    def test_init_1(self) -> None:
        star = SystemStar('VII', 'M', 1)
        self.assertEqual('D', star.size)
        self.assertEqual('M', star.spectral)
        self.assertEqual(1, star.digit)

    def test_str_1(self) -> None:
        star = SystemStar('PSR')
        self.assertEqual('PSR', str(star))

    def test_str_2(self) -> None:
        star = SystemStar('PSR', 'O')
        self.assertEqual('PSR', str(star))

    def test_canonicalise_1(self) -> None:
        star = SystemStar('VI', 'O', 1)
        self.assertEqual('O1 VI', str(star))
        self.assertEqual('O', star.spectral)
        star.canonicalise()
        self.assertEqual('O1 V', str(star))

    def test_canonicalise_2(self) -> None:
        cases = [
            ('Ia', 'F', 2, 'II'),
            ('Ib', 'F', 2, 'II'),
            ('D', 'M', 5, 'V'),
            ('VI', 'O', 5, 'V'),
            ('VI', 'B', 5, 'V'),
            ('VI', 'A', 5, 'V'),
            ('VI', 'F', 0, 'V'),
            ('VI', 'F', 1, 'V'),
            ('VI', 'F', 2, 'V'),
            ('VI', 'F', 3, 'V'),
            ('VI', 'F', 4, 'V'),
            ('IV', 'M', 0, 'V'),
            ('IV', 'K', 5, 'V'),
            ('IV', 'K', 6, 'V'),
            ('IV', 'K', 7, 'V'),
            ('IV', 'K', 8, 'V'),
            ('IV', 'K', 9, 'V')
        ]
        for size, spectral, digit, exp_size in cases:
            with self.subTest():
                star = SystemStar(size, spectral, digit)
                star.canonicalise()
                self.assertEqual(exp_size, star.size)

    def test_check_canonical_1(self) -> None:
        cases = [
            ('Ia', 'F', 2, 'Only OBA class stars can be supergiants (Ia/Ib), not F2 Ia'),
            ('Ib', 'F', 2, 'Only OBA class stars can be supergiants (Ia/Ib), not F2 Ib'),
            ('D', 'M', 5, 'D-size stars with non-empty spectral class _and_ spectral decimal should be V-size, not M5 D'),
            ('VI', 'O', 5, 'OBA class stars cannot be size VI, is O5 VI'),
            ('VI', 'B', 5, 'OBA class stars cannot be size VI, is B5 VI'),
            ('VI', 'A', 5, 'OBA class stars cannot be size VI, is A5 VI'),
            ('VI', 'F', 0, 'F0-F4 class stars cannot be size VI, is F0 VI'),
            ('VI', 'F', 1, 'F0-F4 class stars cannot be size VI, is F1 VI'),
            ('VI', 'F', 2, 'F0-F4 class stars cannot be size VI, is F2 VI'),
            ('VI', 'F', 3, 'F0-F4 class stars cannot be size VI, is F3 VI'),
            ('VI', 'F', 4, 'F0-F4 class stars cannot be size VI, is F4 VI'),
            ('IV', 'M', 0, 'M class stars cannot be size IV, is M0 IV'),
            ('IV', 'K', 5, 'K5-K9 class stars cannot be size IV, is K5 IV'),
            ('IV', 'K', 6, 'K5-K9 class stars cannot be size IV, is K6 IV'),
            ('IV', 'K', 7, 'K5-K9 class stars cannot be size IV, is K7 IV'),
            ('IV', 'K', 8, 'K5-K9 class stars cannot be size IV, is K8 IV'),
            ('IV', 'K', 9, 'K5-K9 class stars cannot be size IV, is K9 IV')
        ]
        for size, spectral, digit, exp_msg in cases:
            with self.subTest():
                star = SystemStar(size, spectral, digit)
                result, msg = star.check_canonical()
                self.assertFalse(result)
                self.assertEqual(exp_msg, msg[0])

    def test_check_canonical_2(self) -> None:
        cases = [
            ('Ia', 'O', 8),
            ('Ia', 'B', 8),
            ('Ia', 'A', 8),
            ('Ib', 'A', 8),
            ('D', 'O', None),
            ('D', None, 6)
        ]
        for size, spectral, digit in cases:
            with self.subTest():
                star = SystemStar(size, spectral, digit)
                result, msg = star.check_canonical()
                self.assertTrue(result)
                self.assertEqual(0, len(msg))

    def test_check_canonical_size(self) -> None:
        star = SystemStar('VI', 'O', 1)
        exp_msg = "Flux values 3 to 8 only permit sizes D IV V of O class star - not VI"
        msg = star.check_canonical_size(8, 3)
        self.assertEqual(exp_msg, msg)

    def test_is_bigger_1(self) -> None:
        cases = [
            ('PSR', None, None, 'BD', None, None, True, False),
            ('PSR', None, None, 'PSR', None, None, True, True),
            ('II', 'O', None, 'II', 'B', None, True, False),
            ('II', 'B', None, 'II', 'B', None, True, True),
            ('II', 'B', 7, 'II', 'B', 8, True, False),
            ('II', 'B', 7, 'II', 'B', 7, True, True),
            ('II', 'B', 6, 'II', None, 6, True, True),
            ('II', 'B', 7, 'II', 'B', None, True, True),
        ]

        for star1_size, star1_spectral, star1_digit, star2_size, star2_spectral, star2_digit, forward, reverse in cases:
            with self.subTest():
                star1 = SystemStar(star1_size, star1_spectral, star1_digit)
                star2 = SystemStar(star2_size, star2_spectral, star2_digit)

                self.assertEqual(forward, star1.is_bigger(star2))
                self.assertEqual(reverse, star2.is_bigger(star1))


if __name__ == '__main__':
    unittest.main()

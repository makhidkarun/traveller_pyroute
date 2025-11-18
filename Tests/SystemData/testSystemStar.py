import unittest

from PyRoute.SystemData.SystemStar import SystemStar


class testSystemStar(unittest.TestCase):
    def test_canonicalise(self) -> None:
        star = SystemStar('VI', 'O', 1)
        self.assertEqual('O1 VI', str(star))
        self.assertEqual('O', star.spectral)
        star.canonicalise()
        self.assertEqual('O1 V', str(star))

    def test_check_canonical_size(self) -> None:
        star = SystemStar('VI', 'O', 1)
        exp_msg = "Flux values 3 to 8 only permit sizes D IV V of O class star - not VI"
        msg = star.check_canonical_size(8, 3)
        self.assertEqual(exp_msg, msg)


if __name__ == '__main__':
    unittest.main()

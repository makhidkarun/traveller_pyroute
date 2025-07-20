import unittest

from PyRoute.Utilities.NoNoneDefaultDict import NoNoneDefaultDict


class testNoNoneDefaultDict(unittest.TestCase):
    def test_reject_none_key(self) -> None:
        foo = NoNoneDefaultDict(int)
        exc = None

        try:
            foo[None] += 1
        except ValueError as e:
            exc = e

        self.assertTrue(isinstance(exc, ValueError), "ValueError not raised")
        self.assertEqual("Supplied key must not be NoneType", exc.args[0])


if __name__ == '__main__':
    unittest.main()

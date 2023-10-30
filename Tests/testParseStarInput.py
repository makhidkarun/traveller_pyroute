import unittest

from PyRoute.Inputs.ParseStarInput import ParseStarInput


class testParseStarInput(unittest.TestCase):

    def test_repack_starline_data(self):
        rawdata = ('0110', '000000000000000', '???????-?', '00000000000000( {1} (000-0)', '     ', None, None, None, ' ', ' ', ' ', '-', '-', '0', '000', ' ', '00', '')

        repack = ParseStarInput.repack_starline_data(rawdata)
        self.assertEqual('{ 1 }', repack[5], "Importance not unpacked from line")
        self.assertEqual('(000-0)', repack[6], "EX not unpacked from line")


if __name__ == '__main__':
    unittest.main()

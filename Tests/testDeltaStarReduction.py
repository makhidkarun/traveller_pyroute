import unittest

from PyRoute.DeltaStar import DeltaStar
from Tests.baseTest import baseTest


class testDeltaStarReduction(baseTest):
    def test_drop_trade_codes_on_none(self):
        src = "0410 Omwyf                B75978A-B                           { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V           Xb:0213 Xb:0609"

        exp = "0410 Omwyf                B75978A-B                           { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V           Xb:0213 Xb:0609                          "
        actual = DeltaStar.reduce(src, drop_trade_codes=True)

        self.assertEqual(exp, actual)

    def test_drop_trade_codes_on_existing(self):
        src = "0216 Ambemshan            A5457BC-B Ag Cp Pi Pz (Cassilldans) { 4 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V"

        exp = "0216 Ambemshan            A5457BC-B                           { 3 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V                                               "
        actual = DeltaStar.reduce(src, drop_trade_codes=True)

        self.assertEqual(exp, actual)

if __name__ == '__main__':
    unittest.main()

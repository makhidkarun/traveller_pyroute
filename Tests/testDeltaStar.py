import unittest

from PyRoute.AreaItems.Sector import Sector
from PyRoute.DeltaStar import DeltaStar
from PyRoute.Star import Star


class testDeltaStar(unittest.TestCase):
    def test_null_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Null reduction unexpected result")

    def test_drop_routes_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_routes=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V                                               "

        self.assertEqual(expected, actual, "Route-drop reduction unexpected result")

    def test_drop_trade_codes_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_trade_codes=True)

        expected = "0240 Bolivar              A78699D-E                                       { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Trade-code-drop reduction unexpected result")

    def test_drop_noble_codes_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_noble_codes=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] -    NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Noble-code-drop reduction unexpected result")

    def test_drop_base_codes_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_base_codes=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF -  A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Base-code-drop reduction unexpected result")

    def test_drop_trade_zone_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_trade_zone=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Trade-zone-drop reduction unexpected result")

    def test_drop_extra_stars_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_extra_stars=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V           Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Star-drop reduction unexpected result")

    def test_reset_pbg_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, reset_pbg=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 100 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Reset-PBG reduction unexpected result")

    def test_reset_worlds_count(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, reset_worlds=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 1  ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Reset-worlds reduction unexpected result")

    def test_reset_port(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, reset_port=True)

        expected = "0240 Bolivar              C78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Reset-port reduction unexpected result")

    def test_reset_tl(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, reset_tl=True)

        expected = "0240 Bolivar              A78699D-8 Asla0 Cp Ga Hi Pr Pz                  { 2 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Reset-TL reduction unexpected result")

    def test_reduce_all(self) -> None:
        check_list = [
            ("0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
             "0240 Bolivar              C78699D-8                                       { 0 }  (G8G+5) [DD9J] -    -  - 100 1  ImDv K1 V                                                    "),
            ('0522 Unchin               A437743-E                            { 2 }  (B6D-1) [492B] B     N  - 620 9  ImDi K0 III                                                       ',
             '0522 Unchin               C437743-8                                       { -1 } (B6D-1) [492B] -    -  - 100 1  ImDi K0 III                                                  '),
            ('1722 Campbell             B99A200-E Lo Wa                                 { 2 }  (812-2) [1419] B    W  - 204 7  ImDv M1 V            Xb:1420 Xb:1823 Xb:2020',
             '1722 Campbell             C99A200-8                                       { -2 } (812-2) [1419] -    -  - 100 1  ImDv M1 V                                                    ')

        ]

        for chunk in check_list:
            with self.subTest():
                original = chunk[0]
                actual = DeltaStar.reduce_all(original)
                expected = chunk[1]

                self.assertEqual(expected, actual, "Reduce-all reduction unexpected result")
                # check if actual can be parsed back into a star
                remix_star = Star.parse_line_into_star(actual, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                self.assertIsInstance(remix_star, Star)

    def test_reduce_sophont_codes(self) -> None:
        check_list = [
            ("0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
             "0240 Bolivar              A78699D-E Cp Ga Hi Pr Pz                        { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "),
            ("2123 Medurma              A9D7954-C An Asla1 Cs Di(Miyavine) Hi S'mr0     { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V",
             "2123 Medurma              A9D7954-C An Cs Hi                              { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                    ")
        ]

        for chunk in check_list:
            with self.subTest():
                original = chunk[0]
                actual = DeltaStar.reduce(original, reset_sophont=True)
                expected = chunk[1]

                self.assertEqual(expected, actual, "Reset-sophont reduction unexpected result")
                # check if actual can be parsed back into a star
                remix_star = Star.parse_line_into_star(actual, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                self.assertIsInstance(remix_star, Star)

    def test_reduce_capitals(self) -> None:
        check_list = [
            ("0240 Bolivar              A78699D-E Cp Ga Hi Pr Pz                       { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
             "0240 Bolivar              A78699D-E Ga Hi Pr Pz                           { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "),
            ("2123 Medurma              A9D7954-C An Cs Hi                             { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                     ",
             "2123 Medurma              A9D7954-C An Hi                                 { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                    "),
            ("2118 Capital              A586A98-F Hi Cx (Syleans)5                     { 4 }  (H9G+4) [AE5F] BEFG  NW - 605 15 ImSy G2 V           Xb:1916 Xb:2021 Xb:2115 Xb:2216 Xb:2218",
             "2118 Capital              A586A98-F (Syleans)5 Hi                         { 4 }  (H9G+4) [AE5F] BEFG NW - 605 15 ImSy G2 V           Xb:1916 Xb:2021 Xb:2115 Xb:2216 Xb:2218  ")
        ]

        for chunk in check_list:
            with self.subTest():
                original = chunk[0]
                old_star = Star.parse_line_into_star(original, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                self.assertTrue(old_star.tradeCode.capital, "Original star should be a capital")

                actual = DeltaStar.reduce(original, reset_capitals=True)
                expected = chunk[1]

                self.assertEqual(expected, actual, "Reset-capital reduction unexpected result")
                # check if actual can be parsed back into a star
                remix_star = Star.parse_line_into_star(actual, Sector('# Core', '# 0, 0'), 'fixed', 'fixed')
                self.assertIsInstance(remix_star, Star)
                self.assertFalse(remix_star.tradeCode.capital, "Remixed star should not be a capital")


if __name__ == '__main__':
    unittest.main()

import copy
import logging
import unittest

from PyRoute.AreaItems.Sector import Sector
from PyRoute.DeltaStar import DeltaStar
from PyRoute.Star import Star


class testDeltaStar(unittest.TestCase):

    def setUp(self) -> None:
        outer_logger = logging.getLogger('PyRoute.Star')
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

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

    def test_drop_routes_reduction_instance(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertEqual(['Xb:0639', 'Xb:Gush-3240', 'Xb:Zaru-0201'], star.routes)

        star.reduce_routes()
        self.assertEqual([], star.routes)

    def test_drop_trade_codes_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, drop_trade_codes=True)

        expected = "0240 Bolivar              A78699D-E                                       { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "

        self.assertEqual(expected, actual, "Trade-code-drop reduction unexpected result")

    def test_drop_trade_codes_reduction_instance(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertEqual('Asla0 Cp Ga Hi Pr Pz', str(star.tradeCode))

        star.reduce_trade_codes()
        self.assertEqual('', str(star.tradeCode))

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
        check_list = [
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V           Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V            Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V           Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V M9 V  Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V           Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
        ]

        for original, expected in check_list:
            with self.subTest():
                actual = DeltaStar.reduce(original, drop_extra_stars=True)
                self.assertEqual(expected, actual, "Star-drop reduction unexpected result")

    def test_trim_trade_zone_reduction(self) -> None:
        check_list = [
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS G 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS U 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS R 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS F 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS U 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
        ]

        for original, expected in check_list:
            with self.subTest():
                actual = DeltaStar.reduce(original, trim_trade_zone=True)
                self.assertEqual(expected, actual, "Trade-zone reduction unexpected result")

    def test_trim_base_code_reduction(self) -> None:
        check_list = [
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF N  - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF N  - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF N  - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF -  - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 3 }  (G8G+5) [DD9J] BcEF -  - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            )
        ]

        for original, expected in check_list:
            with self.subTest():
                actual = DeltaStar.reduce(original, trim_base_codes=True)
                self.assertEqual(expected, actual, "Base-code reduction unexpected result")

    def test_trim_trade_codes_reduction(self) -> None:
        check_list = [
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Cp Hi                                 { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E                                       { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E                                       { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Ag Ni                                 { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Ag Ni                                 { 5 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Na                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Na                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E XXNaXX                                { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E                                       { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Ex                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Ex                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi In                                 { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Hi In                                 { 5 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Ri                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Ri                                    { 5 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Cs                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Cs                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Cx                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Cx                                    { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
        ]

        for original, expected in check_list:
            with self.subTest():
                actual = DeltaStar.reduce(original, trim_trade_codes=True)
                self.assertEqual(expected, actual, "Trade-code reduction unexpected result")

    def test_trim_noble_codes_reduction(self) -> None:
        check_list = [
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] B    NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
            (
                "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] Bc   NS - 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
                "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] B    NS - 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
            ),
        ]

        for original, expected in check_list:
            with self.subTest():
                actual = DeltaStar.reduce(original, trim_noble_codes=True)
                self.assertEqual(expected, actual, "Noble-code reduction unexpected result")

    def test_drop_extra_stars_reduction_instance(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertEqual('K1 V M9 V', str(star.star_list_object))

        star.reduce_extra_stars()
        self.assertEqual('K1 V', str(star.star_list_object))

    def test_reset_pbg_reduction(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        actual = DeltaStar.reduce(original, reset_pbg=True)

        expected = "0240 Bolivar              A78699D-E Asla0 Cp Ga Hi Pr Pz                  { 4 }  (G8G+5) [DD9J] BcEF NS A 100 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        self.assertEqual(expected, actual, "Reset-PBG reduction unexpected result")

    def test_reset_pbg_reduction_instance(self) -> None:
        original = "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        self.assertEqual(8, star.popM)
        self.assertEqual(4, star.ggCount)
        self.assertEqual(1, star.belts)

        star.reduce_pbg()
        self.assertEqual(1, star.popM)
        self.assertEqual(0, star.ggCount)
        self.assertEqual(0, star.belts)

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
            (
            "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
            "0240 Bolivar              C78699D-8                                       { 0 }  (G8G+5) [DD9J] -    -  - 100 1  ImDv K1 V                                                    "),
            (
            '0522 Unchin               A437743-E                            { 2 }  (B6D-1) [492B] B     N  - 620 9  ImDi K0 III                                                       ',
            '0522 Unchin               C437743-8                                       { -1 } (B6D-1) [492B] -    -  - 100 1  ImDi K0 III                                                  '),
            (
            '1722 Campbell             B99A200-E Lo Wa                                 { 2 }  (812-2) [1419] B    W  - 204 7  ImDv M1 V            Xb:1420 Xb:1823 Xb:2020',
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
            (
            "0240 Bolivar              A78699D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
            "0240 Bolivar              A78699D-E Cp Ga Hi Pr Pz                        { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "),
            (
            "2123 Medurma              A9D7954-C An Asla1 Cs Di(Miyavine) Hi S'mr0     { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V",
            "2123 Medurma              A9D7954-C An Cs Hi                              { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                    "),
            (
            "2123 Medurma              A9D7954-C                                       { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V",
            "2123 Medurma              A9D7954-C                                       { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                    "),
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

    def test_reduce_sophont_codes_instance(self) -> None:
        original = "2123 Medurma              A9D7954-C An Asla1 Cs Di(Miyavine) Hi S'mr0     { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V"
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertEqual('An Asla1 Cs Di(Miyavine) Hi S\'mr0', str(star.tradeCode))

        star.reduce_sophonts()
        self.assertEqual('An Cs Hi', str(star.tradeCode))

    def test_reduce_capitals(self) -> None:
        check_list = [
            (
            "0240 Bolivar              A78699D-E Cp Ga Hi Pr Pz                       { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        ",
            "0240 Bolivar              A78699D-E Ga Hi Pr Pz                           { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V      Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "),
            (
            "2123 Medurma              A9D7954-C An Cs Hi                             { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                     ",
            "2123 Medurma              A9D7954-C An Hi                                 { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V                                                    "),
            (
            "2118 Capital              A586A98-F Hi Cx (Syleans)5                     { 4 }  (H9G+4) [AE5F] BEFG  NW - 605 15 ImSy G2 V           Xb:1916 Xb:2021 Xb:2115 Xb:2216 Xb:2218",
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

    def test_check_uwp_1(self) -> None:
        outer_logger = logging.getLogger("PyRoute.Star")
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

        original = "2123 Medurma              A9GB9X4-C An Cs Hi                             { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V"
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertIsNotNone(star, "Starline should be parsed")

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            outer_logger.debug(
                'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
            )
            star.check_canonical()

            output = copy.deepcopy(outer_logs.output)
            exp_logs = [
                'DEBUG:PyRoute.Star:Dummy log entry to shut assertion up now that canonicalisation has been '
                'straightened out',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9GB9X4-C Atmospheric code "G" out '
                'of range - not in range 0-F',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9GB9X4-C Hydrographic code "B" '
                'out of range - not in range 0-A',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9GB9X4-C Calculated government '
                'code "X" out of range - should be 0'
            ]
            self.assertEqual(exp_logs, output)

    def test_check_uwp_2(self) -> None:
        outer_logger = logging.getLogger("PyRoute.Star")
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

        original = "2123 Medurma              A9XX9X4-C An Cs Hi                             { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V"
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertIsNotNone(star, "Starline should be parsed")

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            outer_logger.debug(
                'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
            )
            star.check_canonical()

            output = copy.deepcopy(outer_logs.output)
            exp_logs = [
                'DEBUG:PyRoute.Star:Dummy log entry to shut assertion up now that canonicalisation has been '
                'straightened out',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9XX9X4-C Atmospheric code "X" out '
                'of range - not in range 0-F',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9XX9X4-C Hydrographic code "X" '
                'out of range - not in range 0-A',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9XX9X4-C Calculated government '
                'code "X" out of range - should be 0'
            ]
            self.assertEqual(exp_logs, output)

    def test_check_uwp_3(self) -> None:
        outer_logger = logging.getLogger("PyRoute.Star")
        outer_logger.manager.disable = 0
        outer_logger.setLevel(10)

        original = "2123 Medurma              A9AA9X4-C An Cs Hi                             { 3 }  (G8E+1) [7C3A] -    -  - 100 0  ImDv G0 V"
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertIsNotNone(star, "Starline should be parsed")

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            outer_logger.debug(
                'Dummy log entry to shut assertion up now that canonicalisation has been straightened out'
            )
            star.check_canonical()

            output = copy.deepcopy(outer_logs.output)
            exp_logs = [
                'DEBUG:PyRoute.Star:Dummy log entry to shut assertion up now that canonicalisation has been '
                'straightened out',
                'WARNING:PyRoute.Star:Medurma (dummy 2123)-A9AA9X4-C Calculated government '
                'code "X" out of range - should be 0'
            ]
            self.assertEqual(exp_logs, output)

    def test_check_canonical_instance_good(self) -> None:
        original = "0240 Bolivar              A78699D-E Cp Ga Hi Pr Pz                       { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        msg = []
        actual, msg = star.check_canonical()
        exp_msg = []
        self.assertTrue(actual)
        self.assertEqual(exp_msg, msg)

    def test_check_canonical_instance_bad_1(self) -> None:
        original = "0240 Bolivar              A79789D-E Hi Ga Cp Pr Pz Asla0                  { 4 }  (G8G+5) [DD9J] BcEF NS A 814 11 ImDv K1 V M9 V       Xb:0639 Xb:Gush-3240 Xb:Zaru-0201        "
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        self.assertIsNotNone(star.economics)
        self.assertIsNotNone(star.social)

        exp_msg = [
            'Bolivar (dummy 0240) - EX Calculated labor 8 does not match generated labor 7',
            'Bolivar (dummy 0240) - EX Calculated infrastructure 16 not in range 0 - 15',
            'Bolivar (dummy 0240) - CX Calculated acceptance 13 does not match generated acceptance 11',
            'Bolivar (dummy 0240)-A79789D-E Found invalid "Ga" in trade codes: [\'Ga\', '
            "'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Calculated "Pa" not in trade codes [\'Ga\', '
            "'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Calculated "Pi" not in trade codes [\'Ga\', '
            "'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Found invalid "Pr" in trade codes: [\'Ga\', '
            "'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Calculated "Ph" not in trade codes [\'Ga\', '
            "'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Found invalid "Hi" code on world with 8 '
            "population: ['Ga', 'Hi', 'Pr']",
            'Bolivar (dummy 0240)-A79789D-E Calculated TL "14" not in range 7-12'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_2(self) -> None:
        original = "0101 000000000000000 A000000-0 000000000000000 {0} (000-0) [0000] B A A 000 0 00"
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101) - EX Calculated efficiency 0 should be coded as '
            '1 (implied by p18, book 3 of T5.10)',
            '000000000000000 (dummy 0101)-A000000-0 Calculated "As" not in trade codes []',
            '000000000000000 (dummy 0101)-A000000-0 Calculated "Va" not in trade codes []',
            '000000000000000 (dummy 0101)-A000000-0 Calculated "Ba" not in trade codes []',
            '000000000000000 (dummy 0101)-A000000-0 Calculated TL "0" not in range 11-16'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_3(self) -> None:
        original = '0101 000000000000000 D540000-2 000000000000000       B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101)-D540000-2 Calculated "De" not in trade codes []',
            '000000000000000 (dummy 0101)-D540000-2 Calculated "He" not in trade codes []',
            '000000000000000 (dummy 0101)-D540000-2 Calculated "Po" not in trade codes []',
            '000000000000000 (dummy 0101)-D540000-2 Calculated "Ba" not in trade codes []'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_4(self) -> None:
        original = '0101 000000000000000 ?00?100-6 000000000000000       B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101)-?00?100-6 Calculated "Lo" not in trade codes []'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_5(self) -> None:
        original = '0101 000000000000000 C010400-8 000000000000000 Ni  {0} (006+1) - B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        star.importance = 0

        exp_msg = [
            '000000000000000 (dummy 0101) - EX Calculated labor 0 does not match generated labor 3',
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_6(self) -> None:
        original = '0101 000000000000000 ???????-? 000000000000000 {0} -  [0001] B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101) - CX Calculated symbols 1 should be 0 for barren worlds'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_7(self) -> None:
        original = '0101 000000000000000 A010700-b 000000000000000       B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101)-A010700-B Calculated "Na" not in trade codes []',
            '000000000000000 (dummy 0101)-A010700-B Calculated "Pi" not in trade codes []'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_8(self) -> None:
        original = '0101 000000000000000 A060900-C 000000000000000       B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101)-A060900-C Calculated "De" not in trade codes []',
            '000000000000000 (dummy 0101)-A060900-C Calculated "Pr" not in trade codes []',
            '000000000000000 (dummy 0101)-A060900-C Calculated "Hi" not in trade codes []'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_9(self) -> None:
        original = '0101 000000000000000 ???????-? Na Pi In Pr Pa Ri Ag  {0} -  [0002] B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101) - CX Calculated symbols 2 should be 0 for barren worlds',
            '000000000000000 (dummy 0101)-???????-? Found invalid "In" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Pa" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Ag" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Na" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Pi" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Pr" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']",
            '000000000000000 (dummy 0101)-???????-? Found invalid "Ri" in trade codes: '
            "['Ag', 'In', 'Na', 'Pa', 'Pi', 'Pr', 'Ri']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_10(self) -> None:
        original = '0101 000000000000000 F2G0700-3 Wa Oc Va   {0} -  [0600] B A A 000 0 00'
        sector = Sector("# dummy", "# 0, 0")

        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0101) - CX Calculated homogeneity 0 not in range 2 - 12',
            '000000000000000 (dummy 0101) - CX Calculated strangeness 0 not in range 1 - 10',
            '000000000000000 (dummy 0101) - CX Calculated symbols 0 not in range 1 - 8',
            '000000000000000 (dummy 0101)-F2G0700-3 Found invalid "Oc" in trade codes: '
            "['Oc', 'Va', 'Wa']",
            '000000000000000 (dummy 0101)-F2G0700-3 Found invalid "Va" in trade codes: '
            "['Oc', 'Va', 'Wa']",
            '000000000000000 (dummy 0101)-F2G0700-3 Found invalid "Wa" in trade codes: '
            "['Oc', 'Va', 'Wa']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_11(self) -> None:
        original = '0140 000000000000000 DA4A710-5 As De Ga Fl Ic Po He      - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "As" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "De" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "Fl" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "Ga" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "He" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "Ic" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Found invalid "Po" in trade codes: '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Calculated "Oc" not in trade codes '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']",
            '000000000000000 (dummy 0140)-DA4A710-5 Calculated "Pi" not in trade codes '
            "['As', 'De', 'Fl', 'Ga', 'He', 'Ic', 'Po']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_12(self) -> None:
        original = '0140 000000000000000 ???????-? 000000000000000       De     - A   000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-???????-? Found invalid "De" in trade codes: [\'De\']'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_13(self) -> None:
        original = '0140 000000000000000 ?ADa?00-4 000000000000000       - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-?ADA?00-4 Calculated "Oc" not in trade codes []',
            '000000000000000 (dummy 0140)-?ADA?00-4 Calculated TL "4" not in range 5-10'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_14(self) -> None:
        original = '0140 000000000000000 B2a1710-7 Ba Lo Ni Ph Hi       - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-B2A1710-7 Calculated "Fl" not in trade codes '
            "['Ba', 'Hi', 'Lo', 'Ni', 'Ph']",
            '000000000000000 (dummy 0140)-B2A1710-7 Found invalid "Ba" code on world with '
            "7 population: ['Ba', 'Hi', 'Lo', 'Ni', 'Ph']",
            '000000000000000 (dummy 0140)-B2A1710-7 Found invalid "Lo" code on world with '
            "7 population: ['Ba', 'Hi', 'Lo', 'Ni', 'Ph']",
            '000000000000000 (dummy 0140)-B2A1710-7 Found invalid "Ni" code on world with '
            "7 population: ['Ba', 'Hi', 'Lo', 'Ni', 'Ph']",
            '000000000000000 (dummy 0140)-B2A1710-7 Found invalid "Ph" code on world with '
            "7 population: ['Ba', 'Hi', 'Lo', 'Ni', 'Ph']",
            '000000000000000 (dummy 0140)-B2A1710-7 Found invalid "Hi" code on world with '
            "7 population: ['Ba', 'Hi', 'Lo', 'Ni', 'Ph']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_15(self) -> None:
        original = '0140 000000000000000 B2a1000-0 Ba   {0} (G8E+1)  [1630] - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        exp_msg = [
            '000000000000000 (dummy 0140) - EX Calculated labor 8 does not match generated labor 0',
            '000000000000000 (dummy 0140) - EX Calculated infrastructure 14 does not match generated infrastructure 0',
            '000000000000000 (dummy 0140) - CX Calculated homogeneity 1 should be 0 for barren worlds',
            '000000000000000 (dummy 0140) - CX Calculated acceptance 6 should be 0 for barren worlds',
            '000000000000000 (dummy 0140) - CX Calculated strangeness 3 should be 0 for barren worlds',
            '000000000000000 (dummy 0140)-B2A1000-0 Calculated "Fl" not in trade codes '
            "['Ba']",
            '000000000000000 (dummy 0140)-B2A1000-0 Calculated TL "0" not in range 8-13'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_16(self) -> None:
        original = '0140 000000000000000 B2a1710-7  {0} (G8E+1) [063D] - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        exp_msg = [
            '000000000000000 (dummy 0140) - EX Calculated labor 8 does not match generated labor 6',
            '000000000000000 (dummy 0140) - EX Calculated infrastructure 14 not in range 0 - 12',
            '000000000000000 (dummy 0140) - CX Calculated homogeneity 0 not in range 2 - 12',
            '000000000000000 (dummy 0140) - CX Calculated acceptance 6 does not match generated acceptance 7',
            '000000000000000 (dummy 0140) - CX Calculated symbols 13 not in range 2 - 12',
            '000000000000000 (dummy 0140)-B2A1710-7 Calculated "Fl" not in trade codes []'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_17(self) -> None:
        original = '0140 000000000000000 B2a1310-7 Lo  {0} (G80+1) [C630] - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        star.importance = 0
        exp_msg = [
            '000000000000000 (dummy 0140) - EX Calculated labor 8 does not match generated labor 2',
            '000000000000000 (dummy 0140) - CX Calculated homogeneity 12 not in range 1 - 8',
            '000000000000000 (dummy 0140) - CX Calculated acceptance 6 does not match generated acceptance 3',
            '000000000000000 (dummy 0140) - CX Calculated symbols 0 not in range 2 - 12',
            '000000000000000 (dummy 0140)-B2A1310-7 Calculated "Fl" not in trade codes '
            "['Lo']",
            '000000000000000 (dummy 0140)-B2A1310-7 Calculated TL "7" not in range 8-13'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_18(self) -> None:
        original = '0140 000000000000000 B2a1610-7 Ni  {0} (G87+1) [C630] - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        star.importance = 0
        exp_msg = [
            '000000000000000 (dummy 0140) - EX Calculated labor 8 does not match generated labor 5',
            '000000000000000 (dummy 0140) - EX Calculated infrastructure 7 not in NI range 0 - 6',
            '000000000000000 (dummy 0140) - CX Calculated homogeneity 12 not in range 1 - 11',
            '000000000000000 (dummy 0140) - CX Calculated symbols 0 not in range 2 - 12',
            '000000000000000 (dummy 0140)-B2A1610-7 Calculated "Fl" not in trade codes '
            "['Ni']",
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_19(self) -> None:
        original = '0140 000000000000000 B200610-7 As  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        star.importance = 0
        exp_msg = [
            '000000000000000 (dummy 0140)-B200610-7 Found invalid "As" in trade codes: '
            "['As']",
            '000000000000000 (dummy 0140)-B200610-7 Calculated "Va" not in trade codes '
            "['As']",
            '000000000000000 (dummy 0140)-B200610-7 Calculated "Na" not in trade codes '
            "['As']",
            '000000000000000 (dummy 0140)-B200610-7 Calculated "Ni" not in trade codes '
            "['As']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_20(self) -> None:
        original = '0140 000000000000000 BAA2610-7 He  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-BAA2610-7 Calculated "Fl" not in trade codes '
            "['He']",
            '000000000000000 (dummy 0140)-BAA2610-7 Calculated "Ni" not in trade codes '
            "['He']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_21(self) -> None:
        original = '0140 000000000000000 B998810-7 Pa  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-B998810-7 Calculated "Pi" not in trade codes '
            "['Pa']",
            '000000000000000 (dummy 0140)-B998810-7 Calculated "Ph" not in trade codes '
            "['Pa']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_22(self) -> None:
        original = '0140 000000000000000 B9D2810-7 He  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")

        exp_msg = [
            '000000000000000 (dummy 0140)-B9D2810-7 Found invalid "He" in trade codes: '
            "['He']",
            '000000000000000 (dummy 0140)-B9D2810-7 Calculated "Ph" not in trade codes '
            "['He']"
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_23(self) -> None:
        original = '0140 000000000000000 B9EA810-7 Wa  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        exp_msg = [
            '000000000000000 (dummy 0140)-B9EA810-7 Calculated "Ph" not in trade codes '
            "['Wa']",
            '000000000000000 (dummy 0140)-B9EA810-7 Calculated TL "7" not in range 8-13'
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))

    def test_check_canonical_instance_bad_24(self) -> None:
        original = '0140 000000000000000 B9EA810-8 O:0140 C:0140 Ph Wa  - - - - - A 000   00'
        sector = Sector("# dummy", "# 0, 0")
        star = DeltaStar.parse_line_into_star(original, sector, "fixed", "fixed")
        exp_msg = [
            '000000000000000 (dummy 0140)-B9EA810-8 Found invalid "C:0140" in trade '
            "codes: ['C:0140', 'O:0140', 'Ph', 'Wa']",
            '000000000000000 (dummy 0140)-B9EA810-8 Found invalid "O:0140" in trade '
            "codes: ['C:0140', 'O:0140', 'Ph', 'Wa']",
        ]
        actual, msg = star.check_canonical()
        self.assertFalse(actual)
        self.assertEqual(sorted(exp_msg), sorted(msg))


if __name__ == '__main__':
    unittest.main()

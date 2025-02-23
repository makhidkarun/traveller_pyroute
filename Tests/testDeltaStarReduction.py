import unittest

from PyRoute.DeltaStar import DeltaStar
from Tests.baseTest import baseTest


class testDeltaStarReduction(baseTest):
    def test_drop_trade_codes_on_none(self):
        src = "0410 Omwyf                B75978A-B                           { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V           Xb:0213 Xb:0609"

        exp = "0410 Omwyf                B75978A-B                                       { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V           Xb:0213 Xb:0609                          "
        actual = DeltaStar.reduce(src, drop_trade_codes=True)

        self.assertEqual(exp, actual)

    def test_drop_trade_codes_on_existing(self):
        src = "0216 Ambemshan            A5457BC-B Ag Cp Pi Pz (Cassilldans) { 4 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V"

        exp = "0216 Ambemshan            A5457BC-B                                       { 3 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V                                               "
        actual = DeltaStar.reduce(src, drop_trade_codes=True)

        self.assertEqual(exp, actual)

    def test_reduce_routes_on_none(self):
        src = "0216 Ambemshan            A5457BC-B Ag Cp Pi Pz (Cassilldans) { 4 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V"

        exp = "0216 Ambemshan            A5457BC-B (Cassilldans) Ag Cp Pi Pz             { 4 }  (D6E+5) [AB8E] BCDF NS A 913 10 ImDa M3 V M6 V                                               "
        actual = DeltaStar.reduce(src, drop_routes=True)

        self.assertEqual(exp, actual)

    def test_reduce_routes_on_existing(self):
        src = "0410 Omwyf                B75978A-B                           { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V           Xb:0213 Xb:0609"

        exp = "0410 Omwyf                B75978A-B                                       { 2 }  (D6C+4) [997D] B    N  - 604 9  ImDa G1 V                                                    "
        actual = DeltaStar.reduce(src, drop_routes=True)

        self.assertEqual(exp, actual)

    def test_three_way_combinations_of_reductions(self):
        src = "0627 Taku                 AA676AD-C Ag Ni Ri Cp Da            { 4 }  (B58+5) [AA9G] BCF  NS A 912 14 ImDa K1 V M1 V      Xb:0524 Xb:1029"

        blurb = [
            ("drop_routes, drop_noble_codes, drop_base_codes, drop_trade_zone, reset_pbg, reset_port, reset_tl, reset_capitals",
             "0627 Taku                 CA676AD-8 Ag Da Ni Ri                           { 0 }  (B58+5) [AA9G] -    -  - 100 14 ImDa K1 V M1 V                                               "),
            ("drop_extra_stars, reset_worlds, reset_tl, reset_sophont",
             "0627 Taku                 AA676AD-8 Ag Cp Da Ni Ri                        { 2 }  (B58+5) [AA9G] BCF  NS A 912 1  ImDa K1 V           Xb:0524 Xb:1029                          "),
            ("drop_trade_codes, drop_noble_codes, drop_base_codes, drop_trade_zone, drop_extra_stars, reset_pbg, reset_sophont",
             "0627 Taku                 AA676AD-C                                       { 1 }  (B58+5) [AA9G] -    -  - 100 14 ImDa K1 V           Xb:0524 Xb:1029                          "),
            ("drop_routes, drop_trade_codes, drop_noble_codes, drop_trade_zone, drop_extra_stars, reset_worlds, reset_port, reset_sophont, reset_capitals",
             "0627 Taku                 CA676AD-C                                       { 1 }  (B58+5) [AA9G] -    NS - 912 1  ImDa K1 V                                                    "),
            ("drop_routes, drop_trade_codes, reset_pbg, reset_worlds, reset_capitals",
             "0627 Taku                 AA676AD-C                                       { 2 }  (B58+5) [AA9G] BCF  NS A 100 1  ImDa K1 V M1 V                                               "),
            ("drop_noble_codes, drop_base_codes, reset_worlds, reset_port",
             "0627 Taku                 CA676AD-C Ag Cp Da Ni Ri                        { 2 }  (B58+5) [AA9G] -    -  A 912 1  ImDa K1 V M1 V      Xb:0524 Xb:1029                          "),
            ("drop_routes, drop_trade_codes, drop_trade_zone, drop_extra_stars, reset_tl",
             "0627 Taku                 AA676AD-8                                       { 0 }  (B58+5) [AA9G] BCF  NS - 912 14 ImDa K1 V                                                    "),
            ("drop_trade_codes, drop_base_codes, reset_port, reset_tl, reset_sophont, reset_capitals",
             "0627 Taku                 CA676AD-8                                       { -2 } (B58+5) [AA9G] BCF  -  A 912 14 ImDa K1 V M1 V      Xb:0524 Xb:1029                          "),
            ("drop_routes, reset_pbg, reset_port, reset_sophont",
             "0627 Taku                 CA676AD-C Ag Cp Da Ni Ri                        { 3 }  (B58+5) [AA9G] BCF  NS A 100 14 ImDa K1 V M1 V                                               "),
            ("drop_noble_codes, drop_base_codes, drop_extra_stars, reset_pbg, reset_worlds, reset_tl, reset_capitals",
             "0627 Taku                 AA676AD-8 Ag Da Ni Ri                           { 1 }  (B58+5) [AA9G] -    -  A 100 1  ImDa K1 V           Xb:0524 Xb:1029                          "),
            ("drop_trade_codes, drop_trade_zone, drop_extra_stars, reset_pbg, reset_worlds, reset_port, reset_tl",
             "0627 Taku                 CA676AD-8                                       { -1 } (B58+5) [AA9G] BCF  NS - 100 1  ImDa K1 V           Xb:0524 Xb:1029                          "),
            ("drop_routes, drop_base_codes, drop_trade_zone, drop_extra_stars, reset_pbg, reset_worlds, reset_tl, reset_sophont, reset_capitals",
             "0627 Taku                 AA676AD-8 Ag Da Ni Ri                           { 1 }  (B58+5) [AA9G] BCF  -  - 100 1  ImDa K1 V                                                    "),
            ("drop_noble_codes, drop_trade_zone, reset_capitals",
             "0627 Taku                 AA676AD-C Ag Da Ni Ri                           { 4 }  (B58+5) [AA9G] -    NS - 912 14 ImDa K1 V M1 V      Xb:0524 Xb:1029                          "),
            ("drop_routes, drop_base_codes, drop_extra_stars, reset_port, reset_capitals",
             "0627 Taku                 CA676AD-C Ag Da Ni Ri                           { 2 }  (B58+5) [AA9G] BCF  -  A 912 14 ImDa K1 V                                                    "),
            ("drop_trade_codes, drop_base_codes, drop_trade_zone, reset_pbg, reset_worlds",
             "0627 Taku                 AA676AD-C                                       { 1 }  (B58+5) [AA9G] BCF  -  - 100 1  ImDa K1 V M1 V      Xb:0524 Xb:1029                          "),
            ("drop_routes, drop_trade_codes, drop_noble_codes, drop_extra_stars, reset_pbg, reset_tl",
             "0627 Taku                 AA676AD-8                                       { 0 }  (B58+5) [AA9G] -    NS A 100 14 ImDa K1 V                                                    "),
            ("drop_routes, drop_trade_codes, drop_noble_codes, reset_worlds, reset_port, reset_tl, reset_sophont, reset_capitals",
             "0627 Taku                 CA676AD-8                                       { -1 } (B58+5) [AA9G] -    NS A 912 1  ImDa K1 V M1 V                                               "),
            ("drop_routes, drop_trade_codes, drop_base_codes, drop_trade_zone, reset_worlds, reset_port",
             "0627 Taku                 CA676AD-C                                       { 0 }  (B58+5) [AA9G] BCF  -  - 912 1  ImDa K1 V M1 V                                               ")
        ]

        for msg, expected in blurb:
            with self.subTest(msg):
                bitz = msg.split(', ')
                args = dict()
                for bit in bitz:
                    args[bit] = True
                # Check first pass
                actual = DeltaStar.reduce(src, **args)
                self.assertEqual(expected, actual)
                # Verify reduction is idempotent
                new_actual = DeltaStar.reduce(actual, **args)
                self.assertEqual(actual, new_actual)

    def test_canonicalisation_of_dagudashaag_1722(self):
        src = "1722 Campbell             B99A200-E Lo Wa                                 { 2 }  (812-2) [1419] B    W  - 204 7  ImDv M1 V            Xb:1420 Xb:1823 Xb:2020"
        exp = "1722 Campbell             B99A200-E Lo Wa                                 { 2 }  (812-2) [1419] B    W  - 204 7  ImDv M1 V           Xb:1420 Xb:1823 Xb:2020                  "

        actual = DeltaStar.reduce(src)
        self.assertEqual(exp, actual)

        nu_actual = DeltaStar.reduce(actual)
        self.assertEqual(actual, nu_actual, "Canonicalisation did not round trip")

    def test_canonicalisation_of_dagudashaag_2124(self):
        src = "2123 Medurma              A9D7954-C Hi An Cs Di(Miyavine) Asla1 S'mr0     { 3 }  (G8E+1) [7C3A] BEF  -  - 823 12 ImDv G0 V            Xb:1823 Xb:1926 Xb:2223 Xb:2225 Xb:2322"
        exp = "2123 Medurma              A9D7954-C An Asla1 Cs Di(Miyavine) Hi S'mr0     { 3 }  (G8E+1) [7C3A] BEF  -  - 823 12 ImDv G0 V           Xb:1823 Xb:1926 Xb:2223 Xb:2225 Xb:2322  "

        actual = DeltaStar.reduce(src)
        self.assertEqual(exp, actual)

        nu_actual = DeltaStar.reduce(actual)
        self.assertEqual(actual, nu_actual, "Canonicalisation did not round trip")


if __name__ == '__main__':
    unittest.main()

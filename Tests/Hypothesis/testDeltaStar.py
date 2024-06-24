import unittest

from PyRoute.DeltaStar import DeltaStar
from PyRoute.Galaxy import Sector


class testDeltaStar(unittest.TestCase):

    def test_plain_canonicalisation(self):
        cases = [
            ('0917 Deyis II             E874000-0 Ba Da (Kebkh) Re                      { -3 } (200-5) [0000] -     -  A 000 10 ImDi K4 II                                                        ',
             '0917 Deyis II             E874000-2 Da Di(Kebkh) Re                       { -3 } (200-5) [0000] -     -  A 000 10 ImDi K4 II                                                    '),
            ('0235 Oduart               C7B3004-5 Fl Di(Oduart) Da             { -2 } (800+2) [0000] - M  A 004 10 HvFd G4 V M3 V M7 V',
             '0235 Oduart               C7B3004-5 Ba Da Di(Oduart) Fl                   { -2 } (800+2) [0000] -    M  A 004 10 HvFd G4 V M3 V M7 V                                          '),
            ('0101                      X73A000-0 Ba Lo Ni Wa                         - -  - 012   --',
             '0101                      X73A000-1 Di Wa                                 { -3 } -       -      -     -  - 012 0  --                                                            '),
            ('0527 Wellington Base      AEFA422-E Ht Ni Oc                            - M  R 711   He',
             '0527 Wellington Base      AEFA422-E Ht Ni Oc                              { 1 }  -       -      -     M  R 711 0  He                                                            '),
            ('0239 Etromen              CFB8558-B Fl Ni                               - -  A 523   Na',
             '0239 Etromen              CFB8558-B Fl Ni                                 { 0 }  -       -      -     -  A 523 0  Na                                                            '),
            ('1220 Gateway              A002688-B As Ic Na Ni Va Cx      { 1 }  (C55+1) [675B] - -  - 822 16 GaFd A2 V F0 V',
             '1220 Gateway              A002688-B Cx Ic Na Ni Va                        { 1 }  (C55+1) [675B] -     -  - 822 16 GaFd A2 V F0 V                                                '),
            ('0825 Corstation           C005100-8 As Ic Lo Va            { -2 } (500-5) [1113] - -  - 211 14 GaFd M0 V M1 V',
             '0825 Corstation           C005100-8 Ic Lo Va                              { -2 } (500-5) [1113] -     -  - 211 14 GaFd M0 V M1 V                                                '),
            ('3222 Ardh                           C001554-A As Ic Ni Va          {+0} (843+1) [658A] - C - 601   Ve F9 V',
             '3222 Ardh                 C001554-A Ic Ni Va                              { 0 }  (843+1) [658A] -     C  - 601 0  Ve   F9 V                                                     '),
            ('2738 Taen                           B001685-8 As Ic Ni Na Va       {-1} (J52-2) [3559] - N - 533   Ve M9 V',
             '2738 Taen                 B001685-8 As Ic Na Ni Va                        { -1 } (J52-2) [3559] -    N  - 533 0  Ve   M9 V                                                     '),
            # Population zero, TL 0, alongside a specific dieback should keep the barren
            ('0924 Ognar                X867000-0 Ba Ga Di(Ogna)       {-3 } (300+1) [0000] - -  R 004 10 Og K1 V',
             '0924 Ognar                X867000-0 Ba Di(Ogna) Ga                        { -3 } (300+1) [0000] -     -  R 004 10 Og   K1 V                                                     '),
            # Dieback of two-word sophont name tripped things up
            ('2117 Sabmiqys             A560056-H De Fo Di(Gya Ks)          { 2 }  (600-4) [0000] -    -  R 004 9  ImDa G3 V          ',
             '2117 Sabmiqys             A560056-D De Di(Gya Ks) Fo                      { 1 }  (600-4) [0000] -     -  R 004 9  ImDa G3 V                                                     '),
            # Treat Gov code X as Gov 0
            ('1702 Eslalyat             B493AXB-A Hi In                               - M  R 211   Dr        ',
             '1702 Eslalyat             B493A0B-B Hi In                                 { 4 }  -       -      -     M  R 211 0  Dr                                                            '),
            # <TL8 worlds should have max resources 12
            ('1620 Daydyor Yashas       X683973-D Hi Pr                { 1 }  (E8D+2) [9AAD] - -  - 323 14 NaXX F7 V',
             '1620 Daydyor Yashas       X683973-4 Hi Pr                                 { -1 } (C8B+2) [98A9] -     -  - 323 14 NaXX F7 V                                                     '),
            # Atmo should be capped to F, hydro capped to A
            ('1920 Rainbow Sun          A6VV997-D Hi In Sp                            - KM - 223   Na',
             '1920 Rainbow Sun          A6FA997-D Hi Sp Wa                              { 4 }  -       -      -     KM - 223 0  Na                                                            ')
        ]

        sector = Sector('# Core', '# 0, 0')
        for line, expected in cases:
            with self.subTest():
                foo = DeltaStar.parse_line_into_star(line, sector, 'fixed', 'fixed')
                self.assertIsNotNone(foo, "Line should parse to star")
                foo.canonicalise()
                foo_string = foo.parse_to_line()

                self.assertEqual(expected, foo_string, 'Unexpected canonicalisation result')


if __name__ == '__main__':
    unittest.main()

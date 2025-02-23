"""
Created on Dec 27, 2023

@author: CyberiaResurrection
"""

import unittest

from PyRoute.Inputs.StarlineParser import StarlineParser
from PyRoute.Inputs.StarlineTransformer import StarlineTransformer


class testStarlineParser(unittest.TestCase):
    def test_parser(self):
        txt = '0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  Im M2 V           '
        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0103', transformed[0])
        self.assertEqual('Irkigkhan', transformed[1])
        self.assertEqual('C9C4733-9', transformed[2])
        self.assertEqual('Fl', transformed[3])
        self.assertEqual('{ 0 } (E69+0) [4726]', transformed[4])
        self.assertEqual('{ 0 }', transformed[5])
        self.assertEqual('(E69+0)', transformed[6])
        self.assertEqual('[4726]', transformed[7])
        self.assertEqual('B', transformed[11])
        self.assertEqual('-', transformed[12])
        self.assertEqual('-', transformed[13])
        self.assertEqual('123', transformed[14])
        self.assertEqual('8', transformed[15])
        self.assertEqual('Im', transformed[16])
        self.assertEqual('M2 V', transformed[17])

    def test_parser_missing_extensions(self):
        txt = '2332 Akarrtoog            E300000-0 Ba Na Va                            - K - 013   Kk M1 V                '

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('2332', transformed[0])
        self.assertEqual('Akarrtoog', transformed[1])
        self.assertEqual('E300000-0', transformed[2])
        self.assertEqual('Ba Na Va', transformed[3])
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11])
        self.assertEqual('K', transformed[12])
        self.assertEqual('-', transformed[13])
        self.assertEqual('013', transformed[14])
        self.assertEqual('0', transformed[15])
        self.assertEqual('Kk', transformed[16])
        self.assertEqual('M1 V', transformed[17])

    def test_parser_no_name_and_no_residual(self):
        txt = '0104                      X110000-6 Ba Lo Ni                            - -  - 004   Na'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0104', transformed[0])
        self.assertEqual('', transformed[1])
        self.assertEqual('X110000-6', transformed[2])
        self.assertEqual('Ba Lo Ni', transformed[3])
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11])
        self.assertEqual('-', transformed[12])
        self.assertEqual('-', transformed[13])
        self.assertEqual('004', transformed[14])
        self.assertEqual('0', transformed[15])
        self.assertEqual('Na', transformed[16])
        self.assertEqual('', transformed[17])

    def test_parser_screwball_synthetic_starline_3(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - - - 000 00 00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('00', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_4(self):
        txt = '0101 000000000000000 ???????-? 000000000000000         - Q   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('Q', transformed[12], 'Unexpected base code')
        self.assertEqual('', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_5(self):
        txt = '0101 000000000000000 ???????-? 0000000-0000000       - - a 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('0000000-0000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('A', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_6(self):
        txt = '0101 000000000000000 ?000000-0 000000000000000       - - R 000   000000'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('?000000-0', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('R', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('0000', transformed[16], 'Unexpected allegiance')
        self.assertEqual('00', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_7(self):
        txt = '0101 000000000000000 ???????-? 000000000000000         - F 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('F', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_8(self):
        txt = '0101 000000000000000 ???????-? 000000000000000 {   0} -  [0000] - - F 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('{ 0} - [0000]', transformed[4])
        self.assertEqual('{ 0}', transformed[5])
        self.assertEqual('-', transformed[6])
        self.assertEqual('[0000]', transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('F', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_9(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - - -   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_10(self):
        txt = '0101 000000000000000 ?000000-0 000000000000000       - -      - 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('?000000-0', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_11(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - - A 000   00000 '

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('A', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('0000', transformed[16], 'Unexpected allegiance')
        self.assertEqual('0', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_12(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - -  R   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('R', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_13(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - - g 000  0 00000'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('G', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('0000', transformed[16], 'Unexpected allegiance')
        self.assertEqual('0', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_14(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - -      f 000 0010 00+'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('F', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0010', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('+', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_15(self):
        txt = '0101 000000000000000 ???????-? 000 0000000BCDEFG       - - u 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000 0000000BCDEFG', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('U', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_16(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       - - r 000   10 +'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('R', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('10', transformed[16], 'Unexpected allegiance')
        self.assertEqual('+', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_17(self):
        txt = '0101 000000000000000 ???????-? 000000000000000         -   000   A00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('A00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_18(self):
        txt = '0101 000000000000000 ???????-? 000000000000000         -   001   000'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('001', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('000', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_19(self):
        txt = '0101 000000000000000 ???????-? 000000000000000 {0} - -  - AAA U 000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('{0} - -', transformed[4])
        self.assertEqual('{0}', transformed[5])
        self.assertEqual('-', transformed[6])
        self.assertEqual('-', transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('AAA', transformed[12], 'Unexpected base code')
        self.assertEqual('U', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_20(self):
        txt = '0101 000000000000000      ???????-?                                       { -2 } -       -      -       - 000 0  ?00                                                          '

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('', transformed[3], 'Unexpected trade codes')
        self.assertEqual('{ -2 } - -', transformed[4])
        self.assertEqual('{ -2 }', transformed[5])
        self.assertEqual('-', transformed[6])
        self.assertEqual('-', transformed[7])
        self.assertEqual('', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('?00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_21(self):
        txt = '0101 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]   - a   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)
        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('{0} (000-0) [0000]', transformed[4])
        self.assertEqual('{0}', transformed[5])
        self.assertEqual('(000-0)', transformed[6])
        self.assertEqual('[0000]', transformed[7])
        self.assertEqual('', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('A', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_22(self):
        txt = '0101 000000000000000 ???????-? 000000000000000       c -   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)

        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('000000000000000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('c', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')

    def test_parser_screwball_synthetic_starline_23(self):
        txt = '0101 000000000000000 ???????-? 00000000+  0000         -   000   00'

        foo = StarlineParser()
        result, txt = foo.parse(txt)

        xform = StarlineTransformer(raw=txt)
        transformed = xform.transform(result)

        self.assertTrue(isinstance(transformed, list), "Transformed result not list")
        self.assertEqual('0101', transformed[0], 'Unexpected hex position')
        self.assertEqual('000000000000000', transformed[1], 'Unexpected name')
        self.assertEqual('???????-?', transformed[2], 'Unexpected UWP')
        self.assertEqual('00000000+ 0000', transformed[3], 'Unexpected trade codes')
        self.assertEqual('', transformed[4])
        self.assertEqual(None, transformed[5])
        self.assertEqual(None, transformed[6])
        self.assertEqual(None, transformed[7])
        self.assertEqual('-', transformed[11], 'Unexpected nobles code')
        self.assertEqual('-', transformed[12], 'Unexpected base code')
        self.assertEqual('-', transformed[13], 'Unexpected trade zone')
        self.assertEqual('000', transformed[14], 'Unexpected PBG code')
        self.assertEqual('0', transformed[15], 'Unexpected worlds count')
        self.assertEqual('00', transformed[16], 'Unexpected allegiance')
        self.assertEqual('', transformed[17], 'Unexpected residual')


if __name__ == '__main__':
    unittest.main()

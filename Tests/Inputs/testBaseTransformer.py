"""
Created on Dec 15, 2025

@author: CyberiaResurrection
"""
from lark import Token, Tree

from PyRoute.Inputs.StarlineParser import StarlineParser
from PyRoute.Inputs.StarlineTransformer import StarlineTransformer
from Tests.baseTest import baseTest


class testBaseTransformer(baseTest):

    def test_transform_1(self) -> None:
        original = "0103 Irkigkhan            C9C4733-9 Fl                   { 0 }  (E69+0) [4726] B     - - 123 8  ImDda M2 V           "
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)
        self.assertTrue(transformer.__visit_tokens__)
        self.assertEqual(line, transformer.raw)

        expected = [
            '0103', 'Irkigkhan', 'C9C4733-9', 'Fl', '{ 0 } (E69+0) [4726]', '{ 0 }', '(E69+0)', '[4726]',
            None, None, None, 'B', '-', '-', '123', '8', 'ImDd', 'a M2 V'
        ]
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)

        self.assertEqual(expected, transformed)

    def test_transform_2(self) -> None:
        original = "0101 [0000]000000000 A000000-0 000000000000000000         - - 000   00"
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)

        expected = [
            '0101', '[0000]000000000', 'A000000-0', '000000000000000000', '', None, None, None, ' ',
            ' ', ' ', '', '-', '-', '000', '0', '00', ''
        ]
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)

        self.assertEqual(expected, transformed)

    def test_transform_3(self) -> None:
        result = Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                  Tree(Token('RULE', 'starname'), [Token('__ANON_1', ' Didraga              C1008BC-8 ')]),
                                                  Tree(Token('RULE', 'trade'), [Token('TRADECODE', 'Na'), Token('TRADECODE', 'Va'), Token('TRADECODE', 'Ph'), Token('TRADECODE', 'Pi'), Token('TRADECODE', 'Pz')]),
                                                  Tree(Token('RULE', 'extensions'), [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ -1 }')]), Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(D77+2)')]), Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[B78B]')])]),
                                                  Tree(Token('RULE', 'nbz'), [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', 'BDe')]), Tree(Token('RULE', 'base'), [Token('__ANON_7', 'S ')]), Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'A ')])]),
                                                  Tree(Token('RULE', 'world_alg'), [Tree(Token('RULE', 'pbg'), [Token('__ANON_9', '603 ')]), Tree(Token('RULE', 'worlds'), [Token('__ANON_11', '10 ')]), Tree(Token('RULE', 'allegiance'), [Token('__ANON_12', 'ImDi')])]),
                                                  Tree(Token('RULE', 'residual'), [Token('__ANON_10', ' K0 V                                                         ')])])
        line = ''
        transformer = StarlineTransformer(raw=line)
        expected = [
            '0101', 'Didraga', 'C1008BC-8', 'Na Va Ph Pi Pz', '{ -1 } (D77+2) [B78B]', '{ -1 }', '(D77+2)', '[B78B]',
            None, None, None, 'BDe', 'S', 'A', '603', '10', 'ImDi', 'K0 V'
        ]
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)
        self.assertEqual(expected, transformed)

    def test_transform_4(self) -> None:
        original = "0101 [0000]000000000 A000000-0 000000000000000000         -   000   00"
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)

        expected = [
            '0101', '[0000]000000000', 'A000000-0', '000000000000000000', '', None, None, None, ' ',
            ' ', ' ', '-', '-', '-', '000', '0', '00', ''
        ]
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertTrue(transformer.crankshaft)

        self.assertEqual(expected, transformed)

    def test_transform_5(self) -> None:
        original = "0101 Foobar              A000000-0 Ba Lo Ni Po De He Va As                *   123 8  ImDdab"
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)
        expected = ['0101', 'Foobar', 'A000000-0', 'Ba Lo Ni Po De He Va As', '', None, None, None, ' ', ' ', ' ',
                    '-', '*', '-', '123', '8', 'ImDd', 'ab']
        transformed = transformer.transform(result)
        self.assertEqual(expected, transformed)

    def test_transform_6(self) -> None:
        original = '0101 000000000000000 ???????-? 000000000000000       c -   000   00'
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)
        expected = ['0101', '000000000000000', '???????-?', '000000000000000', '', None, None, None, ' ', ' ', ' ',
                    'c', '-', '', '000', '0', '00', '']
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)
        self.assertEqual(expected, transformed)

    def test_transform_7(self) -> None:
        original = '0101 000000000000000  ?000000-0                 {3 }  (7TG-1) [2IBt]   EHEG -    569 9 C5\''
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)
        expected = ['0101', '000000000000000', '?000000-0', '', '{3 } (7TG-1) [2IBt]', '{3 }', '(7TG-1)', '[2IBt]',
                    None, None, None, 'EHEG', '-', '-', '569', '9', 'C5', '\'']
        transformed = transformer.transform(result)
        self.assertIsNotNone(transformer.crankshaft)
        self.assertFalse(transformer.crankshaft)
        self.assertEqual(expected, transformed)

    def test_transform_8(self) -> None:
        raw = '0101 000000000000000  ?000000-0                 {3 }  (7TG-1) [2IBt]   EHEG -    569 9'
        original = raw + '\n'
        transformer = StarlineTransformer(raw=original)
        self.assertEqual(raw, transformer.raw)

    def test_transform_tree(self) -> None:
        cases = [
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', '000000000000000 ???????-?')]),
                                                 Tree(Token('RULE', 'trade'), [Token('TRADECODE', '000000000000000')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{0}')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000-0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0000]')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'a')])]),
                                                 Tree(Token('RULE', 'world_alg'),
                                                      [Tree(Token('RULE', 'pbg'), [Token('__ANON_9', '000')]),
                                                       Tree(Token('RULE', 'worlds'), [Token('__ANON_11', '0')]),
                                                       Tree(Token('RULE', 'allegiance'), [Token('__ANON_12', '00')])])]),
                ['0101', '000000000000000', '???????-?', '000000000000000', '{0} (000-0) [0000]', '{0}', '(000-0)',
                 '[0000]', None, None, None, '-', '-', 'A', '000', '0', '00', '']
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', '000000000000000 ???????-?')]),
                                                 Tree(Token('RULE', 'trade'), [Token('TRADECODE', '000000000000000')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000-0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0000]')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'a')])]),
                                                 Tree(Token('RULE', 'world_alg'),
                                                      [Tree(Token('RULE', 'pbg'), [Token('__ANON_9', '000')]),
                                                       Tree(Token('RULE', 'worlds'), [Token('__ANON_11', '0')]),
                                                       Tree(Token('RULE', 'allegiance'),
                                                            [Token('__ANON_12', '00')])])]),
                ['0101', '000000000000000', '???????-?', '000000000000000', ' (000-0) [0000]', None, '(000-0)',
                 '[0000]', None, None, None, '-', '-', 'A', '000', '0', '00', '']
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', '000000000000000 ???????-?')]),
                                                 Tree(Token('RULE', 'trade'), [Token('TRADECODE', '000000000000000')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{0}')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0000]')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'a')])]),
                                                 Tree(Token('RULE', 'world_alg'),
                                                      [Tree(Token('RULE', 'pbg'), [Token('__ANON_9', '000')]),
                                                       Tree(Token('RULE', 'worlds'), [Token('__ANON_11', '0')]),
                                                       Tree(Token('RULE', 'allegiance'),
                                                            [Token('__ANON_12', '00')])])]),
                ['0101', '000000000000000', '???????-?', '000000000000000', '{0}   [0000]', '{0}', None,
                 '[0000]', None, None, None, '-', '-', 'A', '000', '0', '00', '']
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', '000000000000000 ???????-?')]),
                                                 Tree(Token('RULE', 'trade'), [Token('TRADECODE', '000000000000000')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{0}')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000-0)')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'a')])]),
                                                 Tree(Token('RULE', 'world_alg'),
                                                      [Tree(Token('RULE', 'pbg'), [Token('__ANON_9', '000')]),
                                                       Tree(Token('RULE', 'worlds'), [Token('__ANON_11', '0')]),
                                                       Tree(Token('RULE', 'allegiance'),
                                                            [Token('__ANON_12', '00')])])]),
                ['0101', '000000000000000', '???????-?', '000000000000000', '{0} (000-0)  ', '{0}', '(000-0)',
                 None, None, None, None, '-', '-', 'A', '000', '0', '00', '']
            )
        ]

        for tree, expected in cases:
            with self.subTest(str(tree)):
                transformer = StarlineTransformer(raw='')
                actual = transformer.transform(tree)
                self.assertEqual(expected, actual)

    def test_starname_transform(self) -> None:
        cases = [
            (' [0000]000000000 A000000-0 ', '[0000]000000000', 'A000000-0'),
            (' Foo Bar A000000-0 ', 'Foo Bar', 'A000000-0'),
            (' Foo  Bar  A000000-0 ', 'Foo Bar', 'A000000-0'),
            (' A B C A000000-0 ', 'A B C', 'A000000-0'),
        ]

        line = ''
        transformer = StarlineTransformer(raw=line)

        for starname, exp_name, exp_uwp in cases:
            with self.subTest(starname):
                act_name, act_uwp = transformer.starname_transform(starname)
                self.assertEqual(exp_name, act_name)
                self.assertEqual(exp_uwp, act_uwp)

    def test_trade_transform(self) -> None:
        cases = [
            (['Ag', 'Ri'], 'Ag Ri')
        ]

        line = ''
        transformer = StarlineTransformer(raw=line)

        for trade_args, exp_trade in cases:
            with self.subTest(trade_args):
                act_trade = transformer.trade_transform(trade_args)
                self.assertEqual(exp_trade, act_trade)

    def test_world_alg_transform(self) -> None:
        cases = [
            (([Token('__ANON_9', '000')], [Token('__ANON_11', ' ')], [Token('__ANON_12', '00')]), ('000', '0', '00')),
            ((['012']), ('0', '1', '2'))
        ]

        line = ''
        transformer = StarlineTransformer(raw=line)
        for world_args, exp_world in cases:
            with self.subTest():
                act_world = transformer.world_alg_transform(world_args)
                self.assertEqual(exp_world, act_world)

    def test_extensions_transform(self) -> None:
        cases = [
            (' ', (None, None, None)),
            ([], (None, None, None)),
            ([Token('ix', '{  +0  }'), Token('ex', '(000+0)')], ('{ +0 }', '(000+0)', None)),
            ([Token('cx', '[0000]'), Token('ex', '(000+0)')], (None, '(000+0)', '[0000]')),
            ([Token('ix', '{  +0  }'), Token('cx', '[0000]')], ('{ +0 }', None, '[0000]')),
            ([Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ -2 }')]),
              Tree(Token('RULE', 'ex'), [Token('__ANON_4', '-')]),
              Tree(Token('RULE', 'cx'), [Token('__ANON_5', '-')])],
             ('{ -2 }', '-', '-'))
        ]
        line = ''
        transformer = StarlineTransformer(raw=line)
        for ext_args, exp_ext in cases:
            with self.subTest(str(ext_args)):
                act_ext = transformer.extensions_transform(ext_args)
                self.assertEqual(exp_ext, act_ext)

    def test_base_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('base', '  ')
        args = [token]
        args = transformer.base(args)
        self.assertEqual('-', args[0].value)

    def test_base_non_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('base', ' / ')
        args = [token]
        args = transformer.base(args)
        self.assertEqual('/', args[0].value)

    def test_nobles_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('nobles', '  ')
        args = [token]
        args = transformer.nobles(args)
        self.assertEqual('-', args[0].value)

    def test_nobles_non_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('nobles', ' / ')
        args = [token]
        args = transformer.nobles(args)
        self.assertEqual('/', args[0].value)

    def test_zone_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('zone', '  ')
        args = [token]
        args = transformer.zone(args)
        self.assertEqual('-', args[0].value)

    def test_zone_non_empty(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('zone', ' A ')
        args = [token]
        args = transformer.zone(args)
        self.assertEqual('A', args[0].value)

    def test_pbg(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('pbg', ' 100 ')
        args = [token]
        args = transformer.pbg(args)
        self.assertEqual('100', args[0].value)

    def test_worlds_long_raw(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('worlds', ' 10 ')
        args = [token]
        args = transformer.worlds(args)
        self.assertEqual('10', args[0].value)

    def test_worlds_short_raw(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('worlds', '1')
        args = [token]
        args = transformer.worlds(args)
        self.assertEqual('1', args[0].value)

    def test_extensions_short_args(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token = Token('ix', '1 ')
        args = [token]
        args = transformer.extensions(args)
        self.assertEqual('1 ', args[0].value)

    def test_extensions_long_args(self) -> None:
        line = ''
        transformer = StarlineTransformer(raw=line)

        token1 = Token('ix', '1 ')
        token2 = Token('cx', '2 ')
        args = [token1, token2]
        args = transformer.extensions(args)
        self.assertEqual('1 ', args[0].value)
        self.assertEqual('2 ', args[1].value)

    def test_starline_1(self) -> None:
        args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                ['Ba', 'Lo', 'Ni', 'Po', 'De', 'He', 'Va', 'As'], [Token('__ANON_2', '     ')],
                Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')], [Token('__ANON_13', '///')]],
                [Token('__ANON_10', 'ab')]]

        line = ''
        transformer = StarlineTransformer(raw=line)

        exp_args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                    ['Ba', 'Lo', 'Ni', 'Po', 'De', 'He'], [Token('__ANON_2', '     ')],
                    Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', 'Va')], [Token('__ANON_7', 'As')], [Token('__ANON_8', '100')]]),
                    [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                    [Token('__ANON_10', 'ab')]
                    ]
        act_args = transformer.starline(args)
        self.assertEqual(str(exp_args), str(act_args))

    def test_starline_2(self) -> None:
        args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                ['Ba', 'Lo', 'Ni', 'Po', 'De', 'He', 'Va', 'As'], [Token('__ANON_2', '     ')],
                Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                [Token('__ANON_10', 'ab')]]

        line = ''
        transformer = StarlineTransformer(raw=line)

        exp_args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                    ['Ba', 'Lo', 'Ni', 'Po', 'De', 'He'], [Token('__ANON_2', '     ')],
                    Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', 'Va')], [Token('__ANON_7', 'As')], [Token('__ANON_8', '100')]]),
                    [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                    [Token('__ANON_10', 'ab')]
                    ]
        act_args = transformer.starline(args)
        self.assertEqual(str(exp_args), str(act_args))

    def test_starline_3(self) -> None:
        args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                ['(Darr)', '(Azha)', 'Va'], [Token('__ANON_2', '     ')],
                Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                [Token('__ANON_10', 'ab')]]

        line = ''
        transformer = StarlineTransformer(raw=line)

        exp_args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                    ['(Darr)', '(Azha)', 'Va'], [Token('__ANON_2', '     ')],
                    Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                    [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                    [Token('__ANON_10', 'ab')]
                    ]
        act_args = transformer.starline(args)
        self.assertEqual(str(exp_args), str(act_args))

    def test_starline_4(self) -> None:
        args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                ['(Darrian)', '(Azhanti)', 'Va'], [Token('__ANON_2', '     ')],
                Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                [Token('__ANON_10', 'ab')]]

        line = ''
        transformer = StarlineTransformer(raw=line)

        exp_args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                    ['(Darrian)'], [Token('__ANON_2', '     ')],
                    Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '(Azhanti)')], [Token('__ANON_7', 'Va')], [Token('__ANON_8', '100')]]),
                    [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                    [Token('__ANON_10', 'ab')]
                    ]
        act_args = transformer.starline(args)
        self.assertEqual(str(exp_args), str(act_args))

    def test_starline_5(self) -> None:
        args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                ['(Darri)', '(Azha)', 'Va'], [Token('__ANON_2', '     ')],
                Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '-')], [Token('__ANON_7', '100')], [Token('__ANON_8', '-')]]),
                [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                [Token('__ANON_10', 'ab')]]

        line = ''
        transformer = StarlineTransformer(raw=line)

        exp_args = [[Token('__ANON_0', '0101')], [Token('__ANON_1', 'Foobar              A000000-0')],
                    ['(Darri)'], [Token('__ANON_2', '     ')],
                    Tree(Token('RULE', 'nbz'), [[Token('__ANON_6', '(Azha)')], [Token('__ANON_7', 'Va')], [Token('__ANON_8', '100')]]),
                    [[Token('__ANON_9', '123')], [Token('__ANON_11', '8')], [Token('__ANON_12', 'ImDd')]],
                    [Token('__ANON_10', 'ab')]
                    ]
        act_args = transformer.starline(args)
        self.assertEqual(str(exp_args), str(act_args))

    def test_trim_raw_string_1(self) -> None:
        transformer = StarlineTransformer(raw='')
        transformer.raw = None
        msg = None

        try:
            transformer.trim_raw_string({})
        except AssertionError as e:
            msg = str(e)
        self.assertEqual('Raw string not supplied before trimming', msg)

    def test_trim_raw_string_2(self) -> None:
        cases = [
            (
                '2926                      B8B2613-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
                {'residual': 'G4 V M1 V', 'position': '2926', 'name': '', 'uwp': 'B8B2613-C',
                 'trade': 'He Fl Ni HakW Pz', 'ix': '{ 1 }', 'ex': '(735+3)', 'cx': '[458B]', 'nobles': '-',
                 'base': 'M', 'zone': 'A', 'pbg': '514', 'worlds': '16', 'allegiance': 'HvFd'},
                ' - M A 514 16 HvFd G4 V M1 V     '
            ),
            (
                '2926                      B8B2613-C He Fl Ni HakW Pz             {     1  } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
                {'ix': '{ 1 }'},
                ' (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     '
            ),
            (
                '2926                      B8B2613-C He Fl Ni HakW Pz             {      1  } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
                {'ix': '{ 1 }'},
                '2926                      B8B2613-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     '
            ),
            (
                ' 2926                      B8B2613-C He Fl Ni HakW Pz             {  1  } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
                {'position': '2926'},
                '                      B8B2613-C He Fl Ni HakW Pz             {  1  } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     '
            ),
            (
                '2926                      B8B2613-C He  Fl            {  1  } (735+3) [458B] - M A 514 16 HeFd G4 V M1 V     ',
                {'uwp': 'X000000-0', 'trade': 'He Fl Ga'},
                '            {  1  } (735+3) [458B] - M A 514 16 HeFd G4 V M1 V     '
            ),
            (
                '2926                      B8B2613-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
                {'name': 'Fnordia'},
                '2926                      B8B2613-C He Fl Ni HakW Pz             {  1 } (735+3) [458B] - M A 514 16 HvFd G4 V M1 V     ',
            )
        ]

        for raw, tree, exp_raw in cases:
            with self.subTest(raw):
                transformer = StarlineTransformer(raw=raw)
                transformer.trim_raw_string(tree)
                self.assertEqual(exp_raw, transformer.raw)

    def test_is_zone(self) -> None:
        cases = [
            ('AR', False),
            ('A', True),
            ('Y', False),
        ]

        for zone_string, expected in cases:
            transformer = StarlineTransformer(raw='')
            actual = transformer.is_zone(zone_string)
            self.assertEqual(expected, actual)

    def test_trim_raw_bitz(self) -> None:
        cases = [
            (
                {'residual': 'M1 V M8 V', 'position': '1309', 'name': 'Selkirk', 'uwp': 'B553420-B', 'trade': 'Ni Po',
                 'ix': '{ 1 }', 'ex': '(A34-3)', 'cx': '[1516]', 'nobles': 'B', 'base': '-', 'zone': '-', 'pbg': '904',
                 'worlds': '12', 'allegiance': 'ImDi'},
                ' B     - - 904 12 ImDi M1 V M8 V                                                    ',
                [' B     - - ',
                 ' 12 ImDi M1 V M8 V                                                    ']
            ),
            (
                {'residual': '', 'position': '0140', 'name': ']00111111111111', 'uwp': '???????-?', 'trade': '',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-', 'zone': '-', 'pbg': '010',
                 'worlds': '0', 'allegiance': '010'},
                '                                                             -    - - 010 0 010                                                          ',
                ['                                                             -    - - ',
                 ' 0 010                                                          '],
            ),
            (
                {'pbg': '010', 'worlds': '010'},
                '                                                             -    - - 010 0 010 ',
                ['                                                             -    - - ', ' 0 010 ']
            ),
            (
                {'pbg': '010', 'worlds': '010'},
                '                                                             -    - - 010',
                ['                                                             -    - - 010 ', ' ']
            ),
            (
                {'pbg': '010', 'worlds': '1', 'allegiance': 'NaHu', 'residual': ''},
                '                                                             -    - - 010 0 010 ',
                ['                                                             -    - - 010 0 ', ' ']
            )
        ]

        for parsed, raw, expected in cases:
            with self.subTest():
                transformer = StarlineTransformer(raw=raw)
                actual = transformer.trim_raw_bitz(parsed)
                self.assertEqual(expected, actual)

    def test_square_up_parsed_zero_1(self) -> None:
        cases = [
            (
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-', 'zone': '-', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'},
                '                               - - - ',
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-', 'zone': '-', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'}
            ),
            (
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-', 'zone': '-', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'},
                '                               - N - ',
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': 'N', 'zone': '-', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'}
            ),
            (
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': 'N', 'zone': 'A', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'},
                '                               - N R ',
                {'residual': 'G9 V', 'position': '2531', 'name': 'Khese', 'uwp': 'C795448-7', 'trade': 'Ni Pa',
                 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': 'N', 'zone': 'R', 'pbg': '803',
                 'worlds': '0', 'allegiance': 'Va'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-',
                 'zone': '-', 'pbg': '001', 'worlds': '0', 'allegiance': '000'},
                '         -   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': '-',
                 'zone': '-', 'pbg': '001', 'worlds': '0', 'allegiance': '000'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': '', 'base': '-',
                 'zone': 'a', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '   - a   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': '', 'base': '-',
                 'zone': 'a', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '00000000000+ 0', 'ix': None, 'ex': None, 'cx': None, 'nobles': '', 'base': '-', 'zone': 'a',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '         - j ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '00000000000+ 0', 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': 'j', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '00000000000+ 0', 'ix': None, 'ex': None, 'cx': None, 'nobles': '', 'base': '-', 'zone': 'a',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '         - AR ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '00000000000+ 0', 'ix': None, 'ex': None, 'cx': None, 'nobles': '-', 'base': 'AR', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': 'c', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '       c -   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': 'c', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': 'c', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '       cs -   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': '', 'base': 'c', 'zone': '-',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': 'c', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '       cs ar   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': 'c', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': '', 'base': '-', 'zone': '',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '       S -   ',
                {'residual': '', 'position': '0101', 'name': '000000000000000', 'uwp': '???????-?',
                 'trade': '000000000000000', 'ix': None, 'ex': None, 'cx': None, 'nobles': '', 'base': '', 'zone': '-',
                 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': '', 'position': '0940', 'name': 'ouV)anTg*V0QDeNL', 'uwp': '???????-?',
                 'trade': ']naJy2GDuB{hq8qG', 'ix': '-', 'ex': '-', 'cx': '[ouJB]', 'nobles': '-', 'base': 'XFX',
                 'zone': '', 'pbg': 'X01', 'worlds': '0', 'allegiance': '11'},
                '  - XFX      ',
                {'residual': '', 'position': '0940', 'name': 'ouV)anTg*V0QDeNL', 'uwp': '???????-?',
                 'trade': ']naJy2GDuB{hq8qG', 'ix': '-', 'ex': '-', 'cx': '[ouJB]', 'nobles': '-', 'base': 'XFX',
                 'zone': '', 'pbg': 'X01', 'worlds': '0', 'allegiance': '11'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BB',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BB A       A      ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BB',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  C A       A      ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'C',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCcDE A             ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCcDE',
                 'base': 'A', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCDEF A             ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCDEF',
                 'base': 'A', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCDE A             ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCDE',
                 'base': 'A', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCDE A  ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCDE',
                 'base': 'A', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': 'A', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCD A             ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCD',
                 'base': 'A', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': '*', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCD A             ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': '*', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': '-', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCD A  ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': '',
                 'base': 'BCD', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
            (
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'A',
                 'base': '-', 'zone': 'A', 'pbg': '000', 'worlds': '0', 'allegiance': '00'},
                '  BCD XXXX  ',
                {'residual': 'C0', 'position': '1010', 'name': '000000000000000', 'uwp': 'A000000-0',
                 'trade': 'Ct00000000000000000', 'ix': '{0}', 'ex': '(000-0)', 'cx': '[0000]', 'nobles': 'BCD',
                 'base': 'XXXX', 'zone': '', 'pbg': '000', 'worlds': '0', 'allegiance': '00'}
            ),
        ]

        for parsed, raw, expected in cases:
            with self.subTest():
                transformer = StarlineTransformer(raw='')
                actual = transformer.square_up_parsed_zero(raw, parsed)
                self.assertEqual(expected, actual)

    def test_square_up_parsed_zero_2(self) -> None:
        transformer = StarlineTransformer(raw='')
        parsed = {'zone': '', 'nobles': ''}
        rawstring = 'BCD N'

        nu_parsed = transformer.square_up_parsed_zero(rawstring, parsed)
        self.assertEqual(parsed, nu_parsed)

    def test_square_up_parsed_zero_3(self) -> None:
        transformer = StarlineTransformer(raw='')
        parsed = {'zone': '-', 'nobles': 'BCD', 'base': 'N'}
        rawstring = 'BCD N - foo'

        nu_parsed = transformer.square_up_parsed_zero(rawstring, parsed)
        self.assertEqual(parsed, nu_parsed)

    def test_square_up_allegiance_overflow(self) -> None:
        cases = [
            ({'allegiance': '----', 'residual': 'Foo'}, {'allegiance': '----', 'residual': 'Foo'}),
            ({'allegiance': '--', 'residual': ''}, {'allegiance': '--', 'residual': ''}),
            ({'allegiance': '----G2V', 'residual': ''}, {'allegiance': '----', 'residual': 'G2V'}),
            ({'allegiance': '--G2V', 'residual': ''}, {'allegiance': '--', 'residual': 'G2V '}),
            ({'allegiance': '--G2', 'residual': ''}, {'allegiance': '--', 'residual': 'G2 '}),
            ({'allegiance': 'ImDd', 'residual': ''}, {'allegiance': 'ImDd', 'residual': ''}),
            ({'allegiance': '?-Z', 'residual': ''}, {'allegiance': '?-Z', 'residual': ''}),
            ({'allegiance': '?-!', 'residual': ''}, {'allegiance': '?-', 'residual': '!'}),
            ({'allegiance': '?-!', 'residual': 'Foo'}, {'allegiance': '?-', 'residual': '! Foo'}),
            ({'allegiance': '/?-!', 'residual': 'Foo'}, {'allegiance': '', 'residual': '/?-! Foo'}),
            ({'allegiance': 'Abcde', 'residual': 'Foo'}, {'allegiance': 'Abcd', 'residual': 'e Foo'}),
        ]
        for parsed, expected in cases:
            with self.subTest():
                transformer = StarlineTransformer(raw='')
                actual = transformer.square_up_allegiance_overflow(parsed)
                self.assertEqual(expected, actual)

    def test_preprocess_trade_and_extensions(self) -> None:
        cases = [
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', 'As'), Token('TRADECODE', 'Ba')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000+0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0001]')])])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', 'As'), Token('TRADECODE', 'Ba')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000+0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0001]')])])])
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'), Token('TRADECODE', 'Ga'),
                                                       Token('TRADECODE', '{0}'), Token('ex', '(000-0)'),
                                                       Token('TRADECODE', '[00G0]'),
                                                       Token('TRADECODE', 'BBB')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'), Token('TRADECODE', 'Ga')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     '),
                                                                                    Token('ix', '{0}'),
                                                                                    Token('ex', '(000-0)'),
                                                                                    Token('cx', '[00G0]'),
                                                                                    Token('TRADECODE', 'BBB')])]),
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'), Token('TRADECODE', 'Ga'),
                                                       Token('TRADECODE', '{0}'), Token('TRADECODE', '(000-0)'),
                                                       ]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'),
                                                       Token('TRADECODE', 'Ga')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     '),
                                                                                    Token('ix', '{0}'),
                                                                                    Token('ex', '(000-0)')])]),
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'), Token('TRADECODE', 'Ga'),
                                                       Token('TRADECODE', '{0}')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'),
                                                       Token('TRADECODE', 'Ga')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     '),
                                                                                    Token('ix', '{0}')])]),
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'), Token('TRADECODE', 'Ga'),
                                                       Token('TRADECODE', '{0}'), Token('ex', '(000-0)'),
                                                       Token('TRADECODE', '[00G0]')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '2340')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 6220]95I3k8??dHT CaA90aC-W ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '6220]95I3k8??dHT'),
                                                       Token('TRADECODE', 'Ga')]),
                                                 Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     '),
                                                                                    Token('ix', '{0}'),
                                                                                    Token('ex', '(000-0)'),
                                                                                    Token('cx', '[00G0]')])]),
            ),
        ]
        for tree, expected in cases:
            with self.subTest(str(tree)):
                transformer = StarlineTransformer(raw='')
                actual = transformer.preprocess_trade_and_extensions(tree)
                self.assertEqual(str(expected.children[3]), str(actual.children[3]))
                self.assertEqual(expected, actual)

    def test_preprocess_tree_suspect_empty_trade_code(self) -> None:
        self.maxDiff = None
        cases = [
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', 'As'), Token('TRADECODE', 'Ba')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000+0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0001]')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'A ')])])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', 'As'), Token('TRADECODE', 'Ba')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')]),
                                                       Tree(Token('RULE', 'ex'), [Token('__ANON_4', '(000+0)')]),
                                                       Tree(Token('RULE', 'cx'), [Token('__ANON_5', '[0001]')])]),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'A ')])])]),
            ),
            (
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', 'De')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [
                                                          Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                      ]
                                                      ),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
                Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                 Tree(Token('RULE', 'starname'),
                                                      [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                                 Tree(Token('RULE', 'trade'),
                                                      [Token('TRADECODE', '')]),
                                                 Tree(Token('RULE', 'extensions'),
                                                      [
                                                          Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                      ]
                                                      ),
                                                 Tree(Token('RULE', 'nbz'),
                                                      [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', 'De')]),
                                                       Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                       Tree(Token('RULE', 'zone'), [Token('__ANON_8', '- ')])])]),
            ),
            (
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', '(Foob)')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', '(Foob)')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
        ),
            (
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcFf')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', '')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 0 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', 'BCcFf')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', '- ')])])]),
        ),
            (
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcFf')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ -1 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcFf')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ -1 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
        ),
            (
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcDFf')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 1 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcDFf')]),
                                             Tree(Token('RULE', 'extensions'),
                                                  [
                                                      Tree(Token('RULE', 'ix'), [Token('__ANON_3', '{ 1 }')])
                                                  ]
                                                  ),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
        ),
            (
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', 'BCcDf')]),
                                             Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')]),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', '-')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '- ')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', 'Q ')])])]),
            Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                             Tree(Token('RULE', 'starname'),
                                                  [Token('__ANON_1', ' 0                    A000000-0 ')]),
                                             Tree(Token('RULE', 'trade'),
                                                  [Token('TRADECODE', '')]),
                                             Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')]),
                                             Tree(Token('RULE', 'nbz'),
                                                  [Tree(Token('RULE', 'nobles'), [Token('__ANON_6', 'BCcDf')]),
                                                   Tree(Token('RULE', 'base'), [Token('__ANON_7', '-')]),
                                                   Tree(Token('RULE', 'zone'), [Token('__ANON_8', '- ')])])]),
        ),
        ]
        for tree, expected in cases:
            with self.subTest(str(tree)):
                transformer = StarlineTransformer(raw='')
                actual = transformer.preprocess_tree_suspect_empty_trade_code(tree)
                self.assertEqual(len(expected.children), len(actual.children))
                i = 0
                while i < len(expected.children):
                    self.assertEqual(str(expected.children[i]), str(actual.children[i]), "Str reps of child " + str(i) + " not equal")
                    self.assertEqual(expected.children[i], actual.children[i], "Child " + str(i) + " not equal")
                    i += 1
                self.assertEqual(expected, actual)

    def test_preprocess_trade_and_extensions_single_extension_1(self) -> None:
        self.maxDiff = None
        transformer = StarlineTransformer(raw='')
        tree = Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                Tree(Token('RULE', 'starname'),
                                                     [Token('__ANON_1', ' 000000000000000 A000000-0 ')]),
                                                Tree(Token('RULE', 'trade'), [Token('TRADECODE',
                                                                                    '[00000000000000 - -  [0000] aa')]),
                                                Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')]),
                                                Tree(Token('RULE', 'nbz'), [Tree(Token('RULE', 'nobles'),
                                                                                 [Token('__ANON_6', 'B')]),
                                                                            Tree(Token('RULE', 'base'),
                                                                                 [Token('__ANON_7', 'A ')]),
                                                                            Tree(Token('RULE', 'zone'),
                                                                                 [Token('__ANON_8', 'A ')])]),
                                                Tree(Token('RULE', 'world_alg'), [Tree(Token('RULE', 'pbg'),
                                                                                       [Token('__ANON_9', '000 ')]),
                                                                                  Tree(Token('RULE', 'worlds'),
                                                                                       [Token('__ANON_11', '0 ')]),
                                                                                  Tree(Token('RULE', 'allegiance'),
                                                                                       [Token('__ANON_12', '00')])])])

        actual = transformer.preprocess_trade_and_extensions(tree)
        trade = actual.children[2]
        exp_trade = Tree(Token('RULE', 'trade'), [Token('TRADECODE', '[00000000000000 - - aa ')])
        self.assertEqual(exp_trade.children[0].value, trade.children[0].value)
        extensions = actual.children[3]
        self.assertEqual(Tree(Token('RULE', 'cx'), [Token('__ANON_3', '[0000]')]), extensions.children[0])

    def test_preprocess_trade_and_extensions_single_extension_2(self) -> None:
        self.maxDiff = None
        transformer = StarlineTransformer(raw='')
        tree = Tree(Token('RULE', 'starline'), [Tree(Token('RULE', 'position'), [Token('__ANON_0', '0101')]),
                                                Tree(Token('RULE', 'starname'),
                                                     [Token('__ANON_1', ' 000000000000000 A000000-0 ')]),
                                                Tree(Token('RULE', 'trade'), [Token('TRADECODE',
                                                                                    '[00000000000000 - -  [AAaa]')]),
                                                Tree(Token('RULE', 'extensions'), [Token('__ANON_2', '     ')])])

        actual = transformer.preprocess_trade_and_extensions(tree)
        extensions = actual.children[3]
        self.assertEqual(Tree(Token('RULE', 'cx'), [Token('__ANON_3', '[AAaa]')]), extensions.children[0])

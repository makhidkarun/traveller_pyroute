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
        original = "0101 Foobar              A000000-0 Ba                  *   123 8  ImDdab"
        parser = StarlineParser()
        result, line = parser.parse(original)
        self.assertIsNotNone(result)

        transformer = StarlineTransformer(raw=line)
        expected = ['0101', 'Foobar', 'A000000-0', 'Ba', '', None, None, None, ' ', ' ', ' ',
                    '-', '*', '-', '123', '8', 'ImDd', 'ab']
        transformed = transformer.transform(result)
        self.assertEqual(expected, transformed)

    def test_starname_transform(self) -> None:
        cases = [
            (' [0000]000000000 A000000-0 ', '[0000]000000000', 'A000000-0'),
            (' Foo Bar A000000-0 ', 'Foo Bar', 'A000000-0'),
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

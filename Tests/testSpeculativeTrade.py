"""
Created on Nov 28, 2024

@author: CyberiaResurrection
"""

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.SpeculativeTrade import SpeculativeTrade
from PyRoute.Star import Star
from Tests.baseTest import baseTest
import unittest


class testSpeculativeTrade(baseTest):
    def test_spec_trade_across_TL(self):
        s = '0101 000000000000000 {} {}  - - A 000   0000D'
        t = '0102 000000000000000 {} {}  - - A 000   0000D'
        pop_code = 'scaled'
        ru_calc = 'scaled'

        cases = [
            ('?000000-0', ['As'], '?000000-1', ['As', 'De'], "CT", 1500, 1400),
            ('?000000-0', ['As'], '?000000-1', ['As', 'De'], "T5", 1500, 1400)
        ]

        for case in cases:
            with self.subTest(msg=case[4]):
                s_actual = s.format(case[0], " ".join(case[1]).ljust(38))
                t_actual = t.format(case[2], " ".join(case[3]).ljust(38))
                trade_type = case[4]
                expSrcPrice = case[5]
                expTrgPrice = case[6]
                sector = Sector('# Core', '# 0, 0')

                foo = Star.parse_line_into_star(s_actual, sector, pop_code, ru_calc)
                foo.index = 1

                bar = Star.parse_line_into_star(t_actual, sector, pop_code, ru_calc)
                bar.index = 2

                galaxy = Galaxy(min_btn=15, max_jump=4)
                galaxy.sectors[sector.name] = sector
                galaxy.star_mapping[1] = foo
                galaxy.star_mapping[2] = bar
                galaxy.stars.add_node(foo.index, star=foo)
                galaxy.stars.add_node(bar.index, star=bar)
                galaxy.stars.add_edge(foo.index, bar.index)
                sector.worlds.append(foo)
                sector.worlds.append(bar)

                spec = SpeculativeTrade(trade_type, galaxy.stars)
                spec.process_tradegoods()

                edge = galaxy.stars.get_edge_data(foo.index, bar.index)
                self.assertEqual(expSrcPrice, edge['SourceMarketPrice'])
                self.assertEqual(expTrgPrice, edge['TargetMarketPrice'])

    def test_spec_trade_same_TL_no_codes(self):
        s = '0101 000000000000000 {} {}  - - A 000   0000D'
        t = '0102 000000000000000 {} {}  - - A 000   0000D'
        pop_code = 'scaled'
        ru_calc = 'scaled'

        cases = [
            ('?000000-0', [], '?000000-0', [], "CT", 1000, 1000),
            ('?000000-0', [], '?000000-0', [], "T5", 1000, 1000),
            ('A000000-0', [], 'X000000-0', [], "CT", 2000, 0),
            ('A000000-0', [], 'X000000-0', [], "T5", 1000, 1000),
            ('B000000-0', [], 'E000000-0', [], "CT", 1000, 0),
            ('B000000-0', [], 'E000000-0', [], "T5", 1000, 1000),
            ('C000000-0', [], 'D000000-0', [], "CT", 0, 0),
            ('C000000-0', [], 'D000000-0', [], "T5", 1000, 1000),
            ('D000000-0', [], 'C000000-0', [], "CT", 0, 0),
            ('D000000-0', [], 'C000000-0', [], "T5", 1000, 1000),
            ('E000000-0', [], 'B000000-0', [], "CT", 0, 1000),
            ('E000000-0', [], 'B000000-0', [], "T5", 1000, 1000),
            ('X000000-0', [], 'A000000-0', [], "CT", 0, 2000),
            ('X000000-0', [], 'A000000-0', [], "T5", 1000, 1000)
        ]

        for case in cases:
            with self.subTest(msg=case[4] + " " + case[0]):
                s_actual = s.format(case[0], " ".join(case[1]).ljust(38))
                t_actual = t.format(case[2], " ".join(case[3]).ljust(38))
                trade_type = case[4]
                expSrcPrice = case[5]
                expTrgPrice = case[6]
                sector = Sector('# Core', '# 0, 0')

                foo = Star.parse_line_into_star(s_actual, sector, pop_code, ru_calc)
                foo.index = 1

                bar = Star.parse_line_into_star(t_actual, sector, pop_code, ru_calc)
                bar.index = 2

                galaxy = Galaxy(min_btn=15, max_jump=4)
                galaxy.sectors[sector.name] = sector
                galaxy.star_mapping[1] = foo
                galaxy.star_mapping[2] = bar
                galaxy.stars.add_node(foo.index, star=foo)
                galaxy.stars.add_node(bar.index, star=bar)
                galaxy.stars.add_edge(foo.index, bar.index)
                sector.worlds.append(foo)
                sector.worlds.append(bar)

                spec = SpeculativeTrade(trade_type, galaxy.stars)
                spec.process_tradegoods()

                edge = galaxy.stars.get_edge_data(foo.index, bar.index)
                self.assertEqual(expSrcPrice, edge['SourceMarketPrice'])
                self.assertEqual(expTrgPrice, edge['TargetMarketPrice'])

    def test_spec_trade_same_TL_with_codes(self):
        s = '0101 000000000000000 {} {}  - - A 000   0000D'
        t = '0102 000000000000000 {} {}  - - A 000   0000D'
        pop_code = 'scaled'
        ru_calc = 'scaled'

        cases = [
            ('?000000-0', ['Ag'], '?000000-0', ['In'], "CT", 3000, 2000),
            ('?000000-0', ['Ag'], '?000000-0', ['In'], "T5", 3000, 3000),
            ('?000000-0', ['As'], '?000000-0', ['Oc'], "CT", 1000, 0),
            ('?000000-0', ['As'], '?000000-0', ['Oc'], "T5", 1000, 0),
            ('?000000-0', ['Ba'], '?000000-0', ['Wa'], "CT", 1000, 0),
            ('?000000-0', ['Ba'], '?000000-0', ['Wa'], "T5", 0, 0),
            ('?000000-0', ['De'], '?000000-0', ['Va'], "CT", 0, 0),
            ('?000000-0', ['De'], '?000000-0', ['Va'], "T5", 0, 0),
            ('?000000-0', ['Fl'], '?000000-0', ['Ri'], "CT", 0, 0),
            ('?000000-0', ['Fl'], '?000000-0', ['Ri'], "T5", 0, 0),
            ('?000000-0', ['Hi'], '?000000-0', ['Po'], "CT", 2000, 2000),
            ('?000000-0', ['Hi'], '?000000-0', ['Po'], "T5", 2000, 1000),
            ('?000000-0', ['Ic'], '?000000-0', ['Ni'], "CT", 1000, 0),
            ('?000000-0', ['Ic'], '?000000-0', ['Ni'], "T5", 1000, 0),
            ('?000000-0', ['In'], '?000000-0', ['Na'], "CT", 1000, 1000),
            ('?000000-0', ['In'], '?000000-0', ['Na'], "T5", 2000, 1000),
            ('?000000-0', ['Lo'], '?000000-0', ['Lo'], "CT", 0, 0),
            ('?000000-0', ['Lo'], '?000000-0', ['Lo'], "T5", 0, 0),
            ('?000000-5', ['Na'], '?000000-5', ['In'], "CT", 500, 500),
            ('?000000-5', ['Na'], '?000000-5', ['In'], "T5", 500, 1500),
            ('?000000-5', ['Ni'], '?000000-5', ['Ic'], "CT", 0, 500),
            ('?000000-5', ['Ni'], '?000000-5', ['Ic'], "T5", 0, 500),
            ('?000000-5', ['Po'], '?000000-5', ['Hi'], "CT", 1500, 1500),
            ('?000000-5', ['Po'], '?000000-5', ['Hi'], "T5", 500, 1500),
            ('?000000-5', ['Ri'], '?000000-5', ['Fl'], "CT", 0, 0),
            ('?000000-5', ['Ri'], '?000000-5', ['Fl'], "T5", 0, 0),
            ('?000000-5', ['Va'], '?000000-5', ['De'], "CT", 0, 0),
            ('?000000-5', ['Va'], '?000000-5', ['De'], "T5", 0, 0),
            ('?000000-5', ['Wa'], '?000000-5', ['Ba'], "CT", 0, 500),
            ('?000000-5', ['Wa'], '?000000-5', ['Ba'], "T5", 0, 0),
            ('?000000-5', ['Oc'], '?000000-5', ['As'], "CT", 0, 500),
            ('?000000-5', ['Oc'], '?000000-5', ['As'], "T5", 0, 500),
        ]

        for case in cases:
            with self.subTest(msg=case[4] + " " + case[0] + " " + " ".join(case[1])):
                s_actual = s.format(case[0], " ".join(case[1]).ljust(38))
                t_actual = t.format(case[2], " ".join(case[3]).ljust(38))
                trade_type = case[4]
                expSrcPrice = case[5]
                expTrgPrice = case[6]
                sector = Sector('# Core', '# 0, 0')

                foo = Star.parse_line_into_star(s_actual, sector, pop_code, ru_calc)
                foo.index = 1

                bar = Star.parse_line_into_star(t_actual, sector, pop_code, ru_calc)
                bar.index = 2

                galaxy = Galaxy(min_btn=15, max_jump=4)
                galaxy.sectors[sector.name] = sector
                galaxy.star_mapping[1] = foo
                galaxy.star_mapping[2] = bar
                galaxy.stars.add_node(foo.index, star=foo)
                galaxy.stars.add_node(bar.index, star=bar)
                galaxy.stars.add_edge(foo.index, bar.index)
                sector.worlds.append(foo)
                sector.worlds.append(bar)

                spec = SpeculativeTrade(trade_type, galaxy.stars)
                spec.process_tradegoods()

                edge = galaxy.stars.get_edge_data(foo.index, bar.index)
                self.assertEqual(expSrcPrice, edge['SourceMarketPrice'])
                self.assertEqual(expTrgPrice, edge['TargetMarketPrice'])


if __name__ == '__main__':
    unittest.main()

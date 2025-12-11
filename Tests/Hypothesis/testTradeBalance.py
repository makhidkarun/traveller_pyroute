"""
Created on Oct 19, 2025

@author: CyberiaResurrection
"""
from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, composite, sampled_from, lists, dictionaries, integers, tuples, SearchStrategy

from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.TradeBalance import TradeBalance
from Tests.baseTest import baseTest


@composite
def multi_dict(draw) -> SearchStrategy:
    sec_names = text(min_size=3, max_size=36, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*')
    sec_strat = lists(sec_names, min_size=2, unique=True)
    choices = draw(sec_strat)
    key_strat = tuples(sampled_from(choices), sampled_from(choices))

    multi_strat = dictionaries(keys=key_strat, values=integers(min_value=0, max_value=2000), min_size=2,
                               max_size=len(choices) * (len(choices) - 1))
    multidict = draw(multi_strat)

    return multidict


class testTradeBalance(baseTest):

    @given(multi_dict())
    @example({('000', '00'): 0, ('000', '0000'): 0})
    @example({('000', '001'): 0, ('000', '002'): 2})
    @example({('8cVH', 'idhC2-TNs'): 1312, ('hnjMin', 'idhC2-TNs'): 1397, ('idhC2-TNs', 'hnjMin'): 376})
    @settings(suppress_health_check=[HealthCheck(10)], deadline=1000)
    def test_multilateral_balance(self, s: dict) -> None:
        galaxy = Galaxy(8)
        for item in s:
            first = item[0]
            second = item[1]
            assume(first != second)
            if first not in galaxy.sectors:
                galaxy.sectors[first] = Sector('# ' + first, '# 0, 0')
            if second not in galaxy.sectors:
                galaxy.sectors[second] = Sector('# ' + second, '# 0, 0')

        foo = TradeBalance(stat_field='tradeExt', region=galaxy)
        foo.update(s)
        foo.multilateral_balance()

        act_dict = dict(foo)
        self.assertTrue(0 <= min(act_dict.values()), "Unexpected minimum value")
        self.assertTrue(1 >= max(act_dict.values()), "Unexpected maximum value")

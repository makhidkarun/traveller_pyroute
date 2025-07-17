import unittest

from AreaItems.AreaItem import AreaItem
from AreaItems.Sector import Sector
from Star import Star
from TradeBalance import TradeBalance


class testTradeBalance(unittest.TestCase):
    def test_trade_balance_add_success(self) -> None:
        foo = TradeBalance(stat_field='passengers', region=AreaItem('name'))
        self.assertEqual(0, len(foo), "Empty TradeBalance should have zero elements")
        key = ('foo', 'bar')
        foo[key] = 1
        self.assertEqual(1, len(foo), "TradeBalance should have 1 element")
        self.assertEqual(1, foo[key])

    def test_log_odd_trade_unit(self) -> None:
        core = Sector('# Core', '# 0, 0')
        dagu = Sector('# Dagudashaag', '# -1, 0')

        star1 = Star()
        star1.sector = core

        star2 = Star()
        star2.sector = dagu

        foo = TradeBalance(stat_field='tradeExt', region=AreaItem('name'))
        foo.log_odd_unit(star1, star2)
        self.assertEqual(1, len(foo), 'TradeBalance should have one element')
        self.assertEqual(1, sum(foo.values()), 'TradeBalance should have unit sum')
        self.assertEqual(0, core.stats.tradeExt, 'Core sector should have no external trade')
        self.assertEqual(0, dagu.stats.tradeExt, 'Dagudashaag sector should have no external trade')

        foo.log_odd_unit(star1, star2)
        self.assertEqual(1, len(foo), 'TradeBalance should have one element')
        self.assertEqual(0, sum(foo.values()), 'TradeBalance should have zero sum')
        self.assertEqual(1, core.stats.tradeExt, 'Core sector should have unit external trade')
        self.assertEqual(1, dagu.stats.tradeExt, 'Dagudashaag sector should have unit external trade')


if __name__ == '__main__':
    unittest.main()

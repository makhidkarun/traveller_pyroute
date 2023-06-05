import unittest

from PyRoute.Galaxy import AreaItem
from PyRoute.TradeBalance import TradeBalance


class testTradeBalance(unittest.TestCase):
    def test_trade_balance_add_success(self):
        item = AreaItem('name')
        foo = TradeBalance(area_item=item)
        self.assertEqual(0, len(foo), "Empty TradeBalance should have zero elements")
        key = ('foo', 'bar')
        foo[key] = 1
        self.assertEqual(1, len(foo), "TradeBalance should have 1 element")
        self.assertEqual(1, foo[key])


if __name__ == '__main__':
    unittest.main()

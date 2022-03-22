import unittest
import sys

sys.path.append('../PyRoute')
from Star import Star
from TradeCalculation import TradeCalculation
from TradeCodes import TradeCodes

param_list = [
    ('A sector capital, B rich sector capital', False, False, True, False, True, False, True, True, 5),
    ('A rich polity capital, B subsector capital', True, False, False, True, False, True, False, False, 4),
    ('A subsector + polity capital, B rich sector capital', False, True, False, True, True, False, True, False, 5),
    ('A rich triple capital, B rich subsector + polity capital', True, True, True, True, True, True, False, True, 6),
    ('A rich subsector capital, B polity capital', True, True, False, False, False, False, False, True, 4),
    ('A sector capital, B rich subsector capital', False, False, True, False, True, True, False, False, 4),
    ('A subsector capital, B triple capital', False, True, False, False, False, True, True, True, 3),
    ('A rich subsector + sector capital, B rich subsector + sector capital', True, True, True, False, True, True, True, False, 6),
    ('A rich polity capital, B rich triple capital', True, False, False, True, True, True, True, True, 6),
    ('A rich sector + polity capital, B sector capital', True, False, True, True, False, False, True, False, 5),
    ('A subsector + sector capital, B nothing', False, True, True, False, False, False, False, False, 2),
    ('A triple capital, B polity capital', False, True, True, True, False, False, False, True, 4),
    ('A rich world, B rich polity capital', True, False, False, False, True, False, False, True, 4),
    ('A polity capital, B subsector + polity capital', False, False, False, True, False, True, False, True, 4),
    ('A nothing, B subsector capital', False, False, False, False, False, True, False, False, 1),
    ('A rich sector + polity capital, B subsector + sector capital', True, False, True, True, False, True, True, False, 5),
    ('All false', False, False, False, False, False, False, False, False, 0),
    ('All true', True, True, True, True, True, True, True, True, 6)
]


class testTradeCalculationPassengerBtn(unittest.TestCase):
    def test_passenger_btn(self):
        for blurb, a_rich, a_subsec, a_sector, a_other, b_rich, b_subsec, b_sector, b_other, expected in param_list:
            with self.subTest(msg=blurb):
                a_string = ''
                if a_rich:
                    a_string += ' Ri'
                if a_subsec:
                    a_string += ' Cp'
                if a_sector:
                    a_string += ' Cs'
                if a_other:
                    a_string += ' Cx'

                b_string = ''
                if b_rich:
                    b_string += ' Ri'
                if b_subsec:
                    b_string += ' Cp'
                if b_sector:
                    b_string += ' Cs'
                if b_other:
                    b_string += ' Cx'

                astar = Star()
                astar.tradeCode = TradeCodes(a_string.strip())
                bstar = Star()
                bstar.tradeCode = TradeCodes(b_string.strip())

                actual = TradeCalculation.get_passenger_btn(0, astar, bstar)
                self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

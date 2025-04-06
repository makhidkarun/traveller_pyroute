import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, composite, sampled_from, lists, floats, booleans, integers

from Position.Hex import Hex
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.TradeCodes import TradeCodes
from PyRoute.Star import Star



@composite
def star_set(draw):
    star1_wtn = draw(integers(min_value=1, max_value=10))
    star2_wtn = draw(integers(min_value=1, max_value=10))

    tradecode = ['', 'Ag', 'In', 'Ni', 'Ex', 'Na']
    star1_trade = draw(sampled_from(tradecode))
    star2_trade = draw(sampled_from(tradecode))

    allegiance = ['Im', 'Na', 'Wild']
    star1_alleg = draw(sampled_from(allegiance))
    star2_alleg = draw(sampled_from(allegiance))

    star1_x = draw(integers(min_value=1, max_value=32))
    star1_y = draw(integers(min_value=1, max_value=32))

    star2_x = draw(integers(min_value=1, max_value=40))
    star2_y = draw(integers(min_value=1, max_value=40))
    if star1_x == star2_x and star1_y == star2_y:
        star2_x = draw(integers(min_value=1, max_value=40))
        star2_y = draw(integers(min_value=1, max_value=40))

    assume(not (star1_x == star2_x and star1_y == star2_y))
    star1_pos = f"{star1_x:02d}{star1_y:02d}"
    star2_pos = f"{star2_x:02d}{star2_y:02d}"

    return star1_wtn, star1_trade, star1_alleg, star1_pos, star2_wtn, star2_trade, star2_alleg, star2_pos


class testTradeCalculationBtn(unittest.TestCase):

    @given(star_set())
    def test_get_btn(self, value):
        star1_wtn, star1_trade, star1_alleg, star1_pos, star2_wtn, star2_trade, star2_alleg, star2_pos = value
        sector = Sector('# Core', '# 0, 0')

        star1 = Star()
        star1.sector = sector
        star1.position = star1_pos
        star1.hex = Hex(sector, star1_pos)
        star1.wtn = star1_wtn
        star1.tradeCode = TradeCodes(star1_trade)
        star1.alg_code = star1_alleg

        star2 = Star()
        star2.sector = sector
        star2.position = star2_pos
        star2.hex = Hex(sector, star2_pos)
        star2.wtn = star2_wtn
        star2.tradeCode = TradeCodes(star2_trade)
        star2.alg_code = star2_alleg

        self.assertTrue(0 < star1.distance(star2))
        self.assertTrue(0 < star2.distance(star1))

        forward_btn = RouteCalculation.get_btn(star1, star2)
        reverse_btn = RouteCalculation.get_btn(star2, star1)

        self.assertEqual(forward_btn, reverse_btn, "Get_btn shouldn't be sensitive to argument ordering")

import unittest

from hypothesis import given, assume
from hypothesis.strategies import composite, sampled_from, integers

from Position.Hex import Hex
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.TradeCodes import TradeCodes
from PyRoute.Star import Star

btn_param_list = [
    (2, 'In', '1620', 'Im', 2, 'In', '3240', 'Im', -1),
    (1, '', '3201', 'Na', 1, 'In', '1620', 'Wild', -5),
    (4, 'Na', '3240', 'Wild', 5, '', '0140', 'Na', 1),
    (2, 'Ni', '0140', 'Na', 4, 'Ni', '0101', 'Na', -1),
    (3, 'In', '0101', 'Wild', 3, 'Ex', '3201', 'Wild', -2),
    (5, 'Ni', '3240', 'Im', 1, '', '3201', 'Im', 0),
    (5, 'In', '0101', 'Na', 2, '', '1620', 'Na', 1),
    (4, 'Ag', '1620', 'Im', 3, '', '0101', 'Wild', 0),
    (1, 'Na', '0140', 'Wild', 3, 'Ni', '1620', 'Im', -3),
    (3, 'Ex', '0140', 'Im', 5, 'In', '3201', 'Na', 1),
    (5, 'Ag', '3201', 'Wild', 4, 'In', '0140', 'Im', 1),
    (4, 'Ex', '0101', 'Na', 4, 'Na', '3240', 'Wild', 0),
    (2, 'Na', '3201', 'Im', 2, 'Ex', '0140', 'Wild', -4),
    (3, 'Ag', '1620', 'Wild', 1, 'Na', '3240', 'Na', -2),
    (3, 'Ni', '3201', 'Na', 5, 'Na', '0101', 'Im', 1),
    (1, 'Ag', '3240', 'Na', 2, 'Ni', '3201', 'Wild', -5),
    (1, 'Ex', '1620', 'Na', 3, '', '0140', 'Im', -2),
    (2, 'In', '3240', 'Wild', 1, 'Ag', '0101', 'Na', -5),
    (1, 'Ag', '0101', 'Im', 5, 'Ex', '1620', 'Na', 0),
    (5, 'Ag', '0140', 'Im', 5, 'Ag', '3240', 'Wild', 2),
    (4, '', '1620', 'Im', 4, 'Na', '3201', 'Im', 3),
    (4, 'In', '3201', 'Im', 1, 'Ni', '0140', 'Na', -1),
    (2, '', '0101', 'Wild', 3, 'Ni', '3240', 'Na', -3),
    (2, 'Ni', '0140', 'Wild', 2, 'Na', '1620', 'Wild', -3),
    (3, 'Na', '0101', 'Na', 4, 'Ag', '3201', 'Im', 1),
    (4, 'Ni', '3240', 'Wild', 3, 'In', '0101', 'Im', 0),
    (5, 'Na', '1620', 'Na', 1, 'Na', '0101', 'Wild', -1),
    (1, 'Ni', '0140', 'Na', 1, 'Ex', '3240', 'Im', -5),
    (3, '', '3240', 'Wild', 2, 'Ex', '0101', 'Im', -3),
    (1, 'In', '3240', 'Wild', 4, 'Na', '0140', 'Im', -3),
    (5, 'Ex', '3240', 'Wild', 5, 'Ni', '1620', 'Im', 3),
    (4, 'Ex', '0140', 'Wild', 2, 'Ag', '1620', 'Wild', -1),
    (5, '', '1620', 'Na', 5, 'Ex', '0140', 'Wild', 3),
    (2, 'Ex', '3201', 'Im', 3, '', '3240', 'Na', -2),
    (5, 'Ni', '1620', 'Na', 3, 'Ag', '0140', 'Im', 2),
    (2, 'Na', '0101', 'Im', 5, 'In', '3240', 'Wild', -1),
    (3, 'Ex', '0101', 'Na', 1, 'Ni', '0140', 'Na', -3),
    (2, '', '0140', 'Wild', 4, '', '3201', 'Im', -2),
    (1, '', '3201', 'Na', 5, 'Ag', '0101', 'Im', -1),
    (4, 'Ex', '0140', 'Wild', 4, 'Ex', '0101', 'Wild', 0),
    (3, 'In', '0140', 'Na', 4, '', '1620', 'Wild', 0),
    (2, 'Ni', '0101', 'Wild', 3, 'Na', '0140', 'Na', -3),
    (4, 'In', '0101', 'Na', 5, 'Ni', '1620', 'Wild', 3),
    (2, 'Ag', '1620', 'Wild', 1, 'Ni', '0140', 'Wild', -4)
]


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

    def test_get_btn_pairwise(self):
        sector = Sector('# Core', '# 0, 0')
        counter = 1
        for star1_wtn, star1_trade, star1_pos, star1_alleg, star2_wtn, star2_trade, star2_pos, star2_alleg, expected in btn_param_list:
            with self.subTest(msg="Subtest " + str(counter)):
                counter += 1
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

                forward_btn = RouteCalculation.get_btn(star1, star2)
                reverse_btn = RouteCalculation.get_btn(star2, star1)

                self.assertEqual(forward_btn, reverse_btn, "Get_btn shouldn't be sensitive to argument ordering")
                self.assertEqual(expected, forward_btn, "Unexpected get-btn value")

    def test_get_max_btn_pairwise(self):
        cases = [
            (0, 0, 1),
            (0, 1, 1),
            (0, 2, 1),
            (0, 3, 1),
            (0, 4, 1),
            (0, 5, 1),
            (1, 1, 3),
            (1, 2, 3),
            (1, 3, 3),
            (1, 4, 3),
            (1, 5, 3),
            (2, 2, 5),
            (2, 3, 5),
            (2, 4, 5),
            (2, 5, 5),
            (3, 3, 7),
            (3, 4, 7),
            (3, 5, 7),
            (4, 4, 9),
            (4, 5, 9),
            (5, 5, 11)
        ]

        counter = 0
        for star1_wtn, star2_wtn, expected in cases:
            counter += 1
            with self.subTest(msg="Subtest " + str(counter)):
                actual = RouteCalculation.get_max_btn(star1_wtn, star2_wtn)
                self.assertEqual(expected, actual)
                actual = RouteCalculation.get_max_btn(star2_wtn, star1_wtn)
                self.assertEqual(expected, actual)
